"""교육용 주식 가상 투자 시뮬레이터: Tkinter + yfinance + Matplotlib."""
from __future__ import annotations

import platform
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
import yfinance as yf
from matplotlib import font_manager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

INITIAL_CASH_KRW = 10_000_000
USD_TO_KRW = 1350.0  # 예시용 고정 환율: 실시간 환율이 아닙니다.


def configure_korean_font() -> None:
    candidates = {
        "Windows": ["Malgun Gothic"],
        "Darwin": ["AppleGothic"],
        "Linux": ["NanumGothic", "Noto Sans CJK KR", "Noto Sans KR"],
    }.get(platform.system(), [])
    available = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((name for name in candidates if name in available), None)
    if selected:
        matplotlib.rcParams["font.family"] = selected
    matplotlib.rcParams["axes.unicode_minus"] = False


class StockSimulator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("나만의 주식 가상 투자 시뮬레이터")
        self.root.geometry("1200x760")
        self.root.minsize(980, 650)
        self.cash = INITIAL_CASH_KRW
        self.portfolio: dict[str, dict[str, float | int]] = {}
        self.price_cache: dict[str, float] = {}
        self.current_ticker = ""
        self.current_price_usd = 0.0
        self.current_price_krw = 0.0
        self.trade_counter = 0
        self.time_steps = [0]
        self.asset_history = [INITIAL_CASH_KRW]
        configure_korean_font()
        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f8f9fa")
        self.style.configure("TLabel", background="#f8f9fa", font=("맑은 고딕", 10))
        self.style.configure("Title.TLabel", font=("맑은 고딕", 16, "bold"))
        for style, color, active in [
            ("Primary.TButton", "#0d6efd", "#0b5ed7"),
            ("Buy.TButton", "#dc3545", "#bb2d3b"),
            ("Sell.TButton", "#198754", "#157347"),
        ]:
            self.style.configure(style, font=("맑은 고딕", 10, "bold"),
                                 foreground="white", background=color, padding=6)
            self.style.map(style, background=[("active", active)])

        main = ttk.Frame(self.root, padding=14)
        main.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(main, padding=(0, 0, 10, 0))
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = ttk.Frame(main, padding=(10, 0, 0, 0))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        search = ttk.LabelFrame(left, text=" 종목 정보 조회 ", padding=10)
        search.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(search, text="미국 주식 티커:").pack(side=tk.LEFT, padx=4)
        self.ticker_entry = ttk.Entry(search, width=10)
        self.ticker_entry.insert(0, "AAPL")
        self.ticker_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(search, text="주가 조회", style="Primary.TButton",
                   command=self.fetch_stock_price).pack(side=tk.LEFT, padx=5)
        self.stock_status_label = ttk.Label(search, text="AAPL, MSFT, TSLA 등 티커 입력")
        self.stock_status_label.pack(side=tk.LEFT, padx=5)

        assets = ttk.LabelFrame(left, text=" 가상 자산 현황 ", padding=10)
        assets.pack(fill=tk.X, pady=(0, 10))
        self.cash_label = self.asset_row(assets, 0, "가용 현금")
        self.stock_label = self.asset_row(assets, 1, "보유 주식 평가액")
        self.total_label = self.asset_row(assets, 2, "총 자산")

        trade = ttk.LabelFrame(left, text=" 가상 매매 ", padding=10)
        trade.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(trade, text="거래 수량(주):").grid(row=0, column=0, padx=4, pady=5)
        self.quantity_entry = ttk.Entry(trade, width=10)
        self.quantity_entry.insert(0, "10")
        self.quantity_entry.grid(row=0, column=1, padx=4, pady=5)
        ttk.Button(trade, text="가상 매수", style="Buy.TButton",
                   command=self.buy).grid(row=1, column=0, sticky="ew", padx=4, pady=5)
        ttk.Button(trade, text="가상 매도", style="Sell.TButton",
                   command=self.sell).grid(row=1, column=1, sticky="ew", padx=4, pady=5)

        holdings = ttk.LabelFrame(left, text=" 보유 종목 ", padding=8)
        holdings.pack(fill=tk.BOTH, expand=True)
        cols = ("ticker", "shares", "avg", "price", "value", "return")
        self.tree = ttk.Treeview(holdings, columns=cols, show="headings", height=8)
        labels = ("티커", "수량", "평단가(원)", "현재가(원)", "평가액(원)", "수익률")
        widths = (65, 55, 95, 95, 105, 70)
        for col, label, width in zip(cols, labels, widths):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        scrollbar = ttk.Scrollbar(holdings, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(right, text="📈 가상 자산 변동 추이", style="Title.TLabel").pack(
            anchor=tk.W, pady=(0, 10))
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        ttk.Label(right, text="교육용 시뮬레이션이며 실제 주문은 전송되지 않습니다.",
                  wraplength=500).pack(anchor=tk.W, pady=8)

    @staticmethod
    def asset_row(parent: ttk.LabelFrame, row: int, title: str) -> ttk.Label:
        ttk.Label(parent, text=title + " (KRW):").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5)
        value = ttk.Label(parent, text="0원", font=("맑은 고딕", 10, "bold"),
                          background="white", relief="groove", padding=5,
                          anchor=tk.E, width=20)
        value.grid(row=row, column=1, sticky=tk.E, padx=8, pady=5)
        return value

    def fetch_stock_price(self) -> None:
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning("입력 오류", "티커를 입력하세요. 예: AAPL")
            return
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            history = yf.Ticker(ticker).history(period="5d", auto_adjust=False)
            if history.empty or history["Close"].dropna().empty:
                raise ValueError("가격 데이터를 찾지 못했습니다. 티커를 확인하세요.")
            price_usd = float(history["Close"].dropna().iloc[-1])
            if price_usd <= 0:
                raise ValueError("유효하지 않은 주가 데이터입니다.")
            price_krw = round(price_usd * USD_TO_KRW)
            self.price_cache[ticker] = float(price_krw)
            self.current_ticker = ticker
            self.current_price_usd = price_usd
            self.current_price_krw = float(price_krw)
            self.stock_status_label.configure(
                text=f"{ticker}: {price_krw:,.0f}원 (USD {price_usd:.2f})",
                foreground="#0d6efd")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("주가 조회 실패",
                f"시세를 가져오지 못했습니다. 티커와 인터넷 연결을 확인하세요.\n\n{exc}")
        finally:
            self.root.config(cursor="")

    def price_for(self, ticker: str, holding: dict[str, float | int]) -> float:
        return self.price_cache.get(ticker, float(holding["avg_price"]))

    def stock_value(self) -> float:
        return sum(int(item["shares"]) * self.price_for(ticker, item)
                   for ticker, item in self.portfolio.items())

    def refresh_all(self) -> None:
        stocks = self.stock_value()
        self.cash_label.configure(text=f"{self.cash:,.0f}원")
        self.stock_label.configure(text=f"{stocks:,.0f}원")
        self.total_label.configure(text=f"{self.cash + stocks:,.0f}원")
        for row in self.tree.get_children():
            self.tree.delete(row)
        for ticker, item in sorted(self.portfolio.items()):
            shares = int(item["shares"])
            avg = float(item["avg_price"])
            price = self.price_for(ticker, item)
            value = shares * price
            rate = (price - avg) / avg * 100 if avg else 0.0
            self.tree.insert("", tk.END, values=(
                ticker, f"{shares:,}", f"{avg:,.0f}", f"{price:,.0f}",
                f"{value:,.0f}", f"{rate:+.2f}%"))
        self.draw_chart()

    def quantity(self) -> int | None:
        try:
            qty = int(self.quantity_entry.get().strip())
            if qty <= 0:
                raise ValueError
            return qty
        except ValueError:
            messagebox.showwarning("수량 오류", "수량은 1 이상의 정수로 입력하세요.")
            return None

    def has_current_price(self) -> bool:
        if not self.current_ticker or self.current_price_krw <= 0:
            messagebox.showwarning("주가 조회 필요", "먼저 티커를 조회하세요.")
            return False
        return True

    def buy(self) -> None:
        if not self.has_current_price():
            return
        qty = self.quantity()
        if qty is None:
            return
        cost = self.current_price_krw * qty
        if cost > self.cash:
            messagebox.showerror("잔액 부족",
                f"매수 금액: {cost:,.0f}원\n가용 현금: {self.cash:,.0f}원")
            return
        ticker = self.current_ticker
        old = self.portfolio.get(ticker, {"shares": 0, "avg_price": 0.0})
        old_shares = int(old["shares"])
        new_shares = old_shares + qty
        new_avg = (old_shares * float(old["avg_price"]) + cost) / new_shares
        self.cash -= cost
        self.portfolio[ticker] = {"shares": new_shares, "avg_price": round(new_avg, 2)}
        self.record_step()
        self.refresh_all()
        messagebox.showinfo("가상 매수 완료",
                            f"{ticker} {qty}주\n매수 금액: {cost:,.0f}원")

    def sell(self) -> None:
        if not self.has_current_price():
            return
        qty = self.quantity()
        if qty is None:
            return
        ticker = self.current_ticker
        holding = self.portfolio.get(ticker)
        if not holding:
            messagebox.showerror("매도 불가", f"{ticker} 보유 수량이 없습니다.")
            return
        shares = int(holding["shares"])
        if qty > shares:
            messagebox.showerror("수량 부족", f"보유 수량: {shares}주\n매도 요청: {qty}주")
            return
        proceeds = self.current_price_krw * qty
        self.cash += proceeds
        if shares == qty:
            del self.portfolio[ticker]
        else:
            holding["shares"] = shares - qty
        self.record_step()
        self.refresh_all()
        messagebox.showinfo("가상 매도 완료",
                            f"{ticker} {qty}주\n매도 금액: {proceeds:,.0f}원")

    def record_step(self) -> None:
        self.trade_counter += 1
        self.time_steps.append(self.trade_counter)
        self.asset_history.append(self.cash + self.stock_value())

    def draw_chart(self) -> None:
        self.ax.clear()
        self.ax.plot(self.time_steps, self.asset_history, marker="o",
                     markersize=5, linewidth=2, color="#0d6efd",
                     label="총 가상 자산(KRW)")
        self.ax.set_title("가상 투자 자산 평가액 추이", fontsize=12, fontweight="bold")
        self.ax.set_xlabel("거래 횟수")
        self.ax.set_ylabel("자산 평가액 (원)")
        self.ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda value, _pos: f"{value:,.0f}"))
        self.ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.legend(loc="best")
        self.fig.tight_layout()
        self.canvas.draw_idle()


def main() -> None:
    root = tk.Tk()
    StockSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

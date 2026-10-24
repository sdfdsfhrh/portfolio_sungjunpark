# 나만의 주식 가상 투자 시뮬레이터

Python의 **Tkinter**, **yfinance**, **Matplotlib**를 활용한 교육용 데스크톱 애플리케이션입니다. 미국 주식 티커를 조회하고 가상 현금으로 매수·매도하며, 보유 종목과 총자산 변화를 그래프로 확인할 수 있습니다.

> **주의:** 실제 증권 주문을 전송하지 않습니다. 조회 가격은 Yahoo Finance에서 가져온 최근 종가이며, 실시간 체결가를 보장하지 않습니다. 원/달러 환율은 예시용 고정값(1 USD = 1,350 KRW)이므로 실시간 환율이나 투자 판단 자료로 사용하지 마세요.

## 주요 기능
- Yahoo Finance 기반 티커 가격 조회 (예: AAPL, MSFT, TSLA, NVDA)
- 원화 기준 가격 환산
- 가상 매수·매도 및 현금 잔액 관리
- 추가 매수 시 가중평균 매입 단가 계산
- 보유 종목별 평가액과 수익률 표시
- 거래 발생 시 총 가상 자산 추이 그래프 갱신
- 거래 수량, 잔액, 보유 수량 입력 검증

## 프로젝트 구조
```text
stock-investment-simulator/
├── README.md
├── requirements.txt
└── stock_investment_simulator.py
```

## 실행 방법
Python 3.10 이상과 인터넷 연결이 필요합니다.

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python stock_investment_simulator.py
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python stock_investment_simulator.py
```

Linux에서는 Tkinter 패키지가 별도로 필요할 수 있습니다. 한글 폰트가 깨지면 Nanum Gothic 또는 Noto Sans CJK KR 글꼴을 설치하세요.

## 구현 기술
- **UI:** Tkinter / ttk
- **시세 데이터:** yfinance
- **차트:** Matplotlib TkAgg
- **상태 관리:** 현금, 보유 수량, 평균 매입가, 조회 종목별 가격 캐시

## 알려진 제한 사항
- 주가 데이터는 지연되거나 누락될 수 있습니다.
- 환율은 고정값이며 수수료, 세금, 배당금은 계산하지 않습니다.
- 프로그램 종료 후 가상 거래 내역은 저장되지 않습니다.
- 조회한 적 없는 보유 종목은 평균 매입가로 평가합니다.
- 투자 성과를 예측하거나 금융 자문을 제공하는 도구가 아닙니다.

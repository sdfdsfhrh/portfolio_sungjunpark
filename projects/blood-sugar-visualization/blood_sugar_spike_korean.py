"""혈당 스파이크 비교 그래프

정제 탄수화물과 통곡물/저GI 식단의 예시 혈당 곡선을 비교합니다.
주의: 그래프의 수치는 설명용으로 직접 만든 가상 데이터이며 임상 자료가 아닙니다.
"""

from pathlib import Path
import platform

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager


def set_korean_font() -> None:
    """운영체제별 한글 글꼴을 설정하고, 가능한 경우 설치된 글꼴을 탐색합니다."""
    system = platform.system()
    preferred = {
        "Windows": ["Malgun Gothic"],
        "Darwin": ["AppleGothic"],
        "Linux": ["NanumGothic", "Noto Sans CJK KR", "Noto Sans KR", "UnDotum"],
    }.get(system, [])

    available = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((name for name in preferred if name in available), None)

    if selected:
        matplotlib.rcParams["font.family"] = selected
    elif system == "Linux":
        print(
            "[안내] 한글 글꼴을 찾지 못했습니다. Ubuntu/Debian에서는 "
            "'sudo apt install fonts-nanum' 실행 후 다시 시도하세요."
        )

    matplotlib.rcParams["axes.unicode_minus"] = False


def build_data() -> pd.DataFrame:
    """비교용 예시 데이터를 DataFrame으로 반환합니다."""
    time_points = np.array(
        [-10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    )
    refined_carb = np.array(
        [90, 92, 130, 175, 190, 185, 155, 125, 95, 80, 75, 78, 82, 88]
    )
    whole_grain = np.array(
        [90, 92, 100, 112, 120, 122, 119, 115, 110, 106, 102, 99, 97, 95]
    )

    return pd.DataFrame(
        {
            "시간(분)": time_points,
            "정제 탄수화물": refined_carb,
            "통곡물/저GI 식단": whole_grain,
        }
    )


def create_chart(
    df: pd.DataFrame,
    output_path: Path | None = None,
    show: bool = True,
) -> Path:
    """그래프를 생성하고 300 DPI PNG로 저장합니다."""
    set_korean_font()

    if output_path is None:
        output_path = Path(__file__).resolve().parent / "blood_sugar_spike_korean.png"

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    # 시각적 참고 범위이며 모든 사람에게 적용되는 임상 기준을 의미하지 않습니다.
    ax.axhspan(70, 140, alpha=0.07, color="green")
    ax.axhline(140, color="#999999", linewidth=0.8, linestyle="--", alpha=0.7)
    ax.axhline(70, color="#999999", linewidth=0.8, linestyle="--", alpha=0.7)
    ax.text(112, 142, "참고 상한: 140 mg/dL", fontsize=8.5, color="#777777", va="bottom")
    ax.text(112, 72, "참고 하한: 70 mg/dL", fontsize=8.5, color="#777777", va="bottom")

    ax.plot(
        df["시간(분)"],
        df["정제 탄수화물"],
        color="#E24B4A",
        linewidth=2.5,
        marker="o",
        markersize=5,
        label="정제 탄수화물 (흰쌀, 빵 등)",
    )
    ax.plot(
        df["시간(분)"],
        df["통곡물/저GI 식단"],
        color="#1D9E75",
        linewidth=2.5,
        marker="s",
        markersize=5,
        label="통곡물 / 저GI 식단",
    )

    peak_idx = df["정제 탄수화물"].idxmax()
    peak_time = int(df.loc[peak_idx, "시간(분)"])
    peak_value = int(df.loc[peak_idx, "정제 탄수화물"])
    ax.annotate(
        f"예시 최고점\n{peak_value} mg/dL",
        xy=(peak_time, peak_value),
        xytext=(peak_time + 12, peak_value + 8),
        arrowprops={"arrowstyle": "->", "color": "#E24B4A", "lw": 1.5},
        fontsize=9.5,
        color="#E24B4A",
        fontweight="bold",
    )

    ax.axvline(0, color="#378ADD", linewidth=1.2, linestyle=":", alpha=0.9)
    ax.text(1.5, 58, "식사 시작", fontsize=9, color="#378ADD", fontweight="bold")

    ax.set_xlabel("식사 후 경과 시간 (분)", fontsize=11, labelpad=8)
    ax.set_ylabel("혈당 농도 (mg/dL)", fontsize=11, labelpad=8)
    ax.set_title(
        "혈당 변화 예시 비교: 정제 탄수화물 vs 통곡물/저GI 식단",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlim(-15, 130)
    ax.set_ylim(50, 215)
    ax.set_xticks(range(-10, 130, 10))
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9, edgecolor="#DDDDDD")
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)

    print(f"저장 완료: {output_path}")
    return output_path


def main() -> None:
    df = build_data()
    create_chart(df)


if __name__ == "__main__":
    main()

# 혈당 스파이크 비교 그래프

정제 탄수화물과 통곡물/저GI 식단을 가정한 두 개의 혈당 변화 곡선을 Python으로 시각화하는 프로젝트입니다. 한글 레이블, 참고 범위 음영, 식사 시점 표시, 최고점 주석을 포함하며 그래프를 300 DPI PNG 파일로 저장합니다.

> **데이터 유의사항:** 그래프의 모든 혈당 수치는 시각화 예시를 위해 직접 작성한 가상 데이터입니다. 실제 관찰·임상 데이터가 아니며, 특정 식품의 효과나 개인의 혈당 반응을 입증하지 않습니다. 논문이나 연구 보고서에 실증 결과로 사용하기 전에 출처가 확인된 데이터를 확보하고 분석 방법과 기준 범위를 검증해야 합니다. 70–140 mg/dL 음영은 시각적 참고용이며 모든 사람과 상황에 적용되는 정상 범위로 해석하면 안 됩니다.

## 미리보기

스크립트를 실행하면 `blood_sugar_spike_korean.png`가 생성됩니다. 생성된 이미지 파일은 이 저장소에 자동 업로드되지 않으며, 필요하면 별도로 커밋하세요.

## 주요 기능

- pandas DataFrame으로 시계열 예시 데이터 구성
- Matplotlib을 이용한 두 곡선 비교
- Windows, macOS, Linux의 한글 폰트 설정
- 식사 시작 시점과 최고점 주석 표시
- 논문 편집용 고해상도(300 DPI) PNG 저장

## 요구 사항

- Python 3.10 이상 권장
- 의존성은 [requirements.txt](requirements.txt) 참고

## 설치 및 실행

프로젝트 폴더에서 다음 명령을 실행합니다.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python blood_sugar_spike_korean.py
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python blood_sugar_spike_korean.py
```

Linux에서 한글이 깨지면 Ubuntu/Debian 계열에서 아래 명령으로 폰트를 설치할 수 있습니다.

```bash
sudo apt install fonts-nanum
```

## 출력

실행하면 프로젝트 폴더에 `blood_sugar_spike_korean.png`가 저장되고 그래프 창이 표시됩니다.

## 프로젝트 구조

```text
blood-sugar-visualization/
├── README.md
├── requirements.txt
└── blood_sugar_spike_korean.py
```

## 다음 개선 아이디어

- 검증된 연구 데이터(CSV) 입력 지원
- 데이터 출처와 측정 조건을 그래프 캡션에 기록
- 평균과 변동성(예: 신뢰구간)을 함께 시각화
- 데이터·코드·그림을 분리해 재현 가능한 분석 흐름 구성

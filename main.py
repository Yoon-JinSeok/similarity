import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="MBTI 유사도 분석", page_icon="🧩", layout="wide")

st.title("🧩 MBTI로 친구와 나 사이의 유사도 구하기")
st.caption("각 단계별로 코드를 확인하고 '실행' 버튼을 눌러 결과를 확인해 보세요.")

# session_state 초기화
if "df" not in st.session_state:
    st.session_state.df = None
if "my_idx" not in st.session_state:
    st.session_state.my_idx = 0


def show_code(code: str):
    st.code(code, language="python")


# =========================================================
# 1단계 : 데이터 불러오기
# =========================================================
st.header("1단계. 데이터 불러오기")
st.markdown(
    "구글 폼으로 수집한 MBTI 검사 결과를 구글 시트에서 **xlsx** 형식으로 다운로드한 뒤, "
    "아래에 업로드하세요."
)

code1 = """# 데이터 불러오기
import pandas as pd

df = pd.read_excel('MBTI 성격유형 검사 결과를 적어주세요.(응답).xlsx')

# 일부 데이터만 출력 (5~12열: MBTI 8개 지표 수치)
df.iloc[:, 4:13]
"""
show_code(code1)

uploaded = st.file_uploader("📂 MBTI 응답 결과 xlsx 파일을 업로드하세요",
                            type=["xlsx"], key="uploader")

col1_1, col1_2 = st.columns([1, 5])
with col1_1:
    run1 = st.button("▶ 1단계 실행", key="run1")

if run1:
    if uploaded is None:
        st.error("먼저 xlsx 파일을 업로드해 주세요.")
    else:
        try:
            df = pd.read_excel(uploaded)
            st.session_state.df = df
            st.success(f"데이터 로드 완료! 총 {len(df)}명의 응답이 저장되었습니다.")
            st.write("**전체 컬럼 목록**")
            st.write(list(df.columns))
            st.write("**df.iloc[:, 4:13] 결과 (MBTI 수치 8개 열)**")
            st.dataframe(df.iloc[:, 4:13])
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")


# =========================================================
# 2단계 : 유클리드 거리 함수
# =========================================================
st.header("2단계. 유클리드 거리 함수 만들기")

code2 = """# 유클리드 거리를 구하는 함수 만들기
import numpy as np

def EuclideanDistance(A, B):
    aryA = np.array(A)   # 배열로 변환
    aryB = np.array(B)   # 배열로 변환
    return (np.sum((aryA - aryB) ** 2)) ** (1 / 2)

# 예시
EuclideanDistance([1, 0], [2, 1])
"""
show_code(code2)


def EuclideanDistance(A, B):
    aryA = np.array(A, dtype=float)
    aryB = np.array(B, dtype=float)
    return (np.sum((aryA - aryB) ** 2)) ** (1 / 2)


st.markdown("**두 벡터 A, B 를 쉼표(,) 로 구분해 입력하세요.**")
c2a, c2b = st.columns(2)
with c2a:
    a_str = st.text_input("A 벡터", value="1, 0", key="euc_A")
with c2b:
    b_str = st.text_input("B 벡터", value="2, 1", key="euc_B")

if st.button("▶ 2단계 실행", key="run2"):
    try:
        A = [float(x) for x in a_str.split(",")]
        B = [float(x) for x in b_str.split(",")]
        if len(A) != len(B):
            st.error("두 벡터의 길이가 같아야 합니다.")
        else:
            d = EuclideanDistance(A, B)
            st.success(f"EuclideanDistance({A}, {B}) = **{d:.6f}**")
    except ValueError:
        st.error("숫자를 쉼표로 구분하여 입력해 주세요. 예) 1, 0")


# =========================================================
# 3단계 : 나와 친구들의 유클리드 거리
# =========================================================
st.header("3단계. 나와 친구들의 유클리드 거리 구하기")

code3 = """# 나의 데이터와 다른 친구들의 유클리드 거리 구하기
my = 0  # 내가 0번 데이터인 경우

myname = df.iloc[my, 4]        # 내 이름
mydata = df.iloc[my, 5:13]     # 내 데이터

for i in df.index:
    e = EuclideanDistance(mydata, df.iloc[i, 5:13])
    print(f'나({myname})와 {df.iloc[i, 4]}의 유클리드 거리 : {e}')
"""
show_code(code3)

if st.session_state.df is not None:
    df = st.session_state.df
    st.session_state.my_idx = st.number_input(
        "내 데이터 번호(행 인덱스)를 선택하세요",
        min_value=0, max_value=len(df) - 1,
        value=st.session_state.my_idx, step=1, key="my_idx_input"
    )
else:
    st.info("먼저 1단계에서 데이터를 업로드해 주세요.")

if st.button("▶ 3단계 실행", key="run3"):
    if st.session_state.df is None:
        st.error("1단계를 먼저 실행해 주세요.")
    else:
        df = st.session_state.df
        my = int(st.session_state.my_idx)
        myname = df.iloc[my, 4]
        mydata = df.iloc[my, 5:13]

        rows = []
        for i in df.index:
            e = EuclideanDistance(mydata.values, df.iloc[i, 5:13].values)
            rows.append({"상대": df.iloc[i, 4], "유클리드 거리": e})
            st.write(f"나({myname})와 **{df.iloc[i, 4]}** 의 유클리드 거리 : `{e:.6f}`")

        result_df = pd.DataFrame(rows).sort_values("유클리드 거리")
        st.markdown("#### 거리순 정렬 결과 (작을수록 가까움)")
        st.dataframe(result_df, use_container_width=True)


# =========================================================
# 4단계 : 코사인 유사도 함수
# =========================================================
st.header("4단계. 코사인 유사도 함수 만들기")

code4 = """# 코사인 유사도 구하는 함수 만들기
def CosineSimilarity(A, B):
    aryA = np.array(A)
    aryB = np.array(B)
    dot = np.sum(aryA * aryB)                     # 내적
    norm_A = (np.sum(aryA ** 2)) ** (1 / 2)       # 벡터의 크기
    norm_B = (np.sum(aryB ** 2)) ** (1 / 2)
    return dot / (norm_A * norm_B)

CosineSimilarity([1, 0], [0, 2])
"""
show_code(code4)


def CosineSimilarity(A, B):
    aryA = np.array(A, dtype=float)
    aryB = np.array(B, dtype=float)
    dot = np.sum(aryA * aryB)
    norm_A = (np.sum(aryA ** 2)) ** (1 / 2)
    norm_B = (np.sum(aryB ** 2)) ** (1 / 2)
    if norm_A == 0 or norm_B == 0:
        return float("nan")
    return dot / (norm_A * norm_B)


c4a, c4b = st.columns(2)
with c4a:
    a4 = st.text_input("A 벡터", value="1, 0", key="cos_A")
with c4b:
    b4 = st.text_input("B 벡터", value="0, 2", key="cos_B")

if st.button("▶ 4단계 실행", key="run4"):
    try:
        A = [float(x) for x in a4.split(",")]
        B = [float(x) for x in b4.split(",")]
        if len(A) != len(B):
            st.error("두 벡터의 길이가 같아야 합니다.")
        else:
            c = CosineSimilarity(A, B)
            st.success(f"CosineSimilarity({A}, {B}) = **{c:.6f}**")
    except ValueError:
        st.error("숫자를 쉼표로 구분하여 입력해 주세요.")


# =========================================================
# 5단계 : 나와 친구들의 코사인 유사도
# =========================================================
st.header("5단계. 나와 친구들의 코사인 유사도 구하기")

code5 = """# 나의 데이터와 다른 친구들의 코사인 유사도 구하기
for i in df.index:
    c = CosineSimilarity(mydata, df.iloc[i, 5:13])
    print(f'나({myname})와 {df.iloc[i, 4]}의 코사인 유사도 : {c}')
"""
show_code(code5)

if st.button("▶ 5단계 실행", key="run5"):
    if st.session_state.df is None:
        st.error("1단계를 먼저 실행해 주세요.")
    else:
        df = st.session_state.df
        my = int(st.session_state.my_idx)
        myname = df.iloc[my, 4]
        mydata = df.iloc[my, 5:13]

        rows = []
        for i in df.index:
            c = CosineSimilarity(mydata.values, df.iloc[i, 5:13].values)
            rows.append({"상대": df.iloc[i, 4], "코사인 유사도": c})
            st.write(f"나({myname})와 **{df.iloc[i, 4]}** 의 코사인 유사도 : `{c:.6f}`")

        result_df = pd.DataFrame(rows).sort_values("코사인 유사도", ascending=False)
        st.markdown("#### 유사도순 정렬 결과 (1에 가까울수록 유사)")
        st.dataframe(result_df, use_container_width=True)


# =========================================================
# 6단계 : MBTI 글자(E/I, S/N, T/F, J/P) 일부 데이터 추출
# =========================================================
st.header("6단계. MBTI 글자 데이터 추출하기")

code6 = """# 일부 데이터만 추출 (이름과 MBTI 4가지 지표 문자)
df.iloc[:, [4, 13, 14, 15, 16]]
"""
show_code(code6)

if st.button("▶ 6단계 실행", key="run6"):
    if st.session_state.df is None:
        st.error("1단계를 먼저 실행해 주세요.")
    else:
        df = st.session_state.df
        st.dataframe(df.iloc[:, [4, 13, 14, 15, 16]], use_container_width=True)


# =========================================================
# 7단계 : 자카드 유사도 함수
# =========================================================
st.header("7단계. 자카드 유사도 함수 만들기")

code7 = """# 자카드 유사도를 구하는 함수 만들기
def JaccardSimilarity(A, B):
    SetA = set(A)
    SetB = set(B)
    union = len(SetA | SetB)            # 합집합 원소 개수
    intersection = len(SetA & SetB)     # 교집합 원소 개수
    return intersection / union

JaccardSimilarity(['a', 'b', 'c'], ['b', 'a', 'f', 'g'])
"""
show_code(code7)


def JaccardSimilarity(A, B):
    SetA = set(A)
    SetB = set(B)
    union = len(SetA | SetB)
    if union == 0:
        return float("nan")
    intersection = len(SetA & SetB)
    return intersection / union


c7a, c7b = st.columns(2)
with c7a:
    a7 = st.text_input("A (쉼표로 구분된 문자들)", value="a, b, c", key="jac_A")
with c7b:
    b7 = st.text_input("B (쉼표로 구분된 문자들)", value="b, a, f, g", key="jac_B")

if st.button("▶ 7단계 실행", key="run7"):
    A = [x.strip() for x in a7.split(",") if x.strip() != ""]
    B = [x.strip() for x in b7.split(",") if x.strip() != ""]
    if not A or not B:
        st.error("문자들을 쉼표로 구분하여 입력해 주세요.")
    else:
        j = JaccardSimilarity(A, B)
        st.success(f"JaccardSimilarity({A}, {B}) = **{j:.6f}**")


# =========================================================
# 8단계 : 나와 친구들의 자카드 유사도
# =========================================================
st.header("8단계. 나와 친구들의 자카드 유사도 구하기")

code8 = """# 나의 데이터와 다른 친구들의 자카드 유사도 구하기
mydataJ = df.iloc[my, 13:17]   # 나의 MBTI 4글자
for i in df.index:
    j = JaccardSimilarity(mydataJ, df.iloc[i, 13:17])
    print(f'나({myname})와 {df.iloc[i, 4]}의 자카드 유사도 : {j}')
"""
show_code(code8)

if st.button("▶ 8단계 실행", key="run8"):
    if st.session_state.df is None:
        st.error("1단계를 먼저 실행해 주세요.")
    else:
        df = st.session_state.df
        my = int(st.session_state.my_idx)
        myname = df.iloc[my, 4]
        mydataJ = df.iloc[my, 13:17]

        rows = []
        for i in df.index:
            j = JaccardSimilarity(mydataJ.values, df.iloc[i, 13:17].values)
            rows.append({"상대": df.iloc[i, 4], "자카드 유사도": j})
            st.write(f"나({myname})와 **{df.iloc[i, 4]}** 의 자카드 유사도 : `{j:.6f}`")

        result_df = pd.DataFrame(rows).sort_values("자카드 유사도", ascending=False)
        st.markdown("#### 유사도순 정렬 결과 (1에 가까울수록 유사)")
        st.dataframe(result_df, use_container_width=True)


st.markdown("---")
st.caption("© MBTI Similarity Demo · Streamlit")

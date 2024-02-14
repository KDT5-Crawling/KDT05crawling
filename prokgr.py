from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn
from nltk import sent_tokenize, word_tokenize, pos_tag
from googletrans import Translator

import csv
import os
import pandas as pd
import nltk

nltk.download('sentiwordnet')
nltk.download('book')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('vader_lexicon')

# 간단한 NLTK PennTreebank Tag를 기반으로 WordNet 기반의 품사 Tag로 변환
def penn_to_wn(tag):
    if tag.startswith('J'):
        return wn.ADJ
    elif tag.startswith('N'):
        return wn.NOUN
    elif tag.startswith('R'):
        return wn.ADV
    elif tag.startswith('V'):
        return wn.VERB

def swn_polarity(text):
    # 감성 지수 초기화
    sentiment = 0.0
    tokens_count = 0

    lemmatizer = WordNetLemmatizer()
    raw_sentences = sent_tokenize(text)
    # 분해된 문장별로 단어 토큰 -> 품사 태깅 후에 SentiSynset 생성 -> 감성 지수 합산
    for raw_sentence in raw_sentences:
        # NTLK 기반의 품사 태깅 문장 추출
        tagged_sentence = pos_tag(word_tokenize(raw_sentence))
        for word, tag in tagged_sentence:

            # WordNet 기반 품사 태깅과 어근 추출
            wn_tag = penn_to_wn(tag)
            if wn_tag not in (wn.NOUN, wn.ADJ, wn.ADV):
                continue
            lemma = lemmatizer.lemmatize(word, pos=wn_tag)
            if not lemma:
                continue
            # 어근을 추출한 단어와 WordNet 기반 품사 태깅을 입력해 Synset 객체를 생성.
            synsets = wn.synsets(lemma, pos=wn_tag)
            if not synsets:
                continue
            # sentiwordnet의 감성 단어 분석으로 감성 synset 추출
            # 모든 단어에 대해 긍정 감성 지수는 +로 부정 감성 지수는 -로 합산해 감성 지수 계산.
            synset = synsets[0]
            swn_synset = swn.senti_synset(synset.name())
            sentiment += (swn_synset.pos_score() - swn_synset.neg_score())
            tokens_count += 1

    if not tokens_count:
        return 0

    # 총 score가 0 이상일 경우 긍정(Positive) 1, 그렇지 않을 경우 부정(Negative) 0 반환
    if sentiment >= 0:
        return 1

    return 0

total_list = []
data_list = [
"[단독]'학생수 위기' 종로 효제초교 안에 아파트 짓는다…'주교복합' 첫 모델",
"모건스탠리, 자산관리 부서에서 수백명 감원",
"“동방오거리에 도시철도역 신설”…장예찬 예비후보, 3대 공약 발표",
"올해 경남도정, 도민들에게 한 발 더 다가간다",
"윤석열 정부 초라한 ‘경제 성적표’, 총선 표심 변수 될까",
"시스코, 올해 인력 5% 해고…AI·소프트웨어 등 고성장 사업 집중",
"달랑 2명 접수, 지방 아파트는 ‘미분양' 늪?…“공주·포항 그래도 될 곳은 ...",
"AI신인류, 국가간 격차 확대할 것…통제 필요하지만 공존법 있어",
"인플레이션감축법 폐기 선언에… 전기차 산업 ‘초비상’",
"[저출산 연속기고 ②] 왜 초저출산 국가가 됐나",
"[현장칼럼] 기로에선 창원특례시와 함안군 통합,태어나는 사람은 적은 데다가 양질의 <b>일자리</b>와 문화가 있는 수도권으로 젊은이들",
"총선 후보, 기후위기 대응 공약 내놔야",
"전남 올 노인복지 예산 1조 6000억,노인<b>일자리</b>는 7000명이 늘어난 6만 4000명으로",
"[사설]저출산에 노동인구까지 <b>감소</b>…중장년층 고용지원 강화해야",
"노동인구 <b>감소</b>로 중장년층 계속 고용 불가피",
"[폐광 그 후 - 다시 찾은 미래] 2. 폐광→실직 반복되는 폐광지역",
"[해외ESG트렌드] 미국 ESG 채용 붐 시대 재조정기 접어들어",
"거창군, 교육발전특구 시범지역 1유형 경남도 내 최초 도전",
"익산시, 옛 전북 명품 교육도시 조성 박차",
"'도민과 소통' 행정 만족도 크게 높인다",
"고부가가치 <b>일자리</b> 창출 청년 유출 방지",
"스마트 복지·웰다잉 문화 선도…시니어 문화의 기준 될 것",
"도내 총선 후보, 기후위기 대책 제시해야",
"노동인구 부족에… 중장년 재취업 교육 지원 필요",
"‘수수’ 등 농림부산물, 신재생에너지 연료자원으로 부각",
"전남도, 1조6천억 투입 노인복지 챙긴다",
"경주역 부지에 상징물 세워 세계적 명소로",
"생태 정원도시 다음은 ‘K디즈니’… 순천의 도전은 계속된다 [지방기획]",
"노동시장 여성 심리적 고통 해소부터",
"조선업종 등 구인난 해소에 중장년층 적극 활용을",
"익산시, 명품 교육도시 조성 박차",
"박성호 국힘 김해갑 예비후보, '청년정책' 공약 발표",
"장시간 근로자, OECD 평균 수준 줄어",
"함안군 '인구증가 가능지역'...경남 인구<b>감소</b>지역마다 원인도 풀 열쇠도 달라",
"원도심·신도심 공존… 인프라 개선으로 격차 줄인다",
"인구<b>감소</b> 원인 하나하나 따졌더니…지역별 족집게 대책 나왔다",
"경기·경북·전남 '경제효과 3조' 이민청 유치전,이민청을 유치할 경우 3000명의 <b>일자리</b> 창출과 3조원 이상의 경제효과",
"어르신이 행복하고 편안한 전남 역량 모은다",
"[대일응접실] 김동일 보령시장 글로벌 해양레저관광·탄소중립·보령형 포용...",
"답안보이는 '수도권 쏠림'…인구·취업자수·기업체 절반 이상 넘어",
"[전남일보]전남도, 올해 1조6천억 투입 노인복지사업 추진",
"[중앙로365] 이민청 유치, 부산만 잠잠",
"국민은행 콜센터노동자들 AI로 업무강도 높아져···고용불안도 여전",
"거창군, 경남도 내 최초 '교육발전특구 시범지역' 도전",
"경남도, 도민 만족도 높이는 정책 추진…민원콜센터 서비스 확대",
"[2024 희망! 경남시대] 생동감과 활기 넘치는 모두가 행복한 산청 건설에 총...",
"익산시, 명품 교육도시 조성 박차",
"도민들에게 한 발 더 다가가는 도정 추진 박차",
"'국경 폐쇄' 외쳐야 민심 얻는다?… ‘이민자 나라’ 미국에서 왜 ‘반이민...",
"거창군 '교육발전특구 시범지역 1유형' 도전…경남 최초",
"김성회 예비후보 &quot;동남4군, 충청메가시티 배후관광지로 육성&quot;",
"전남 재정자립도, 전국 평균의 절반···지방 소멸 가속 우려",
"제주살이 열풍의 종말···자연에 이끌렸다가, 현실에 질려 떠난다",
"거창군, 교육발전 시범지역 1유형 '도전장'",
"김원이 더불어민주당 목포시 예비후보",
"현대차·기아…'주주환원+규제완화+실적'",
"예상원 경남도의원, 밀양시장 도전",
"경남도, 도민과 소통하는 도정 '박차'",
"대전시민 삶의 만족도 높아졌다",
"거창군, 경남 최초 ‘교육발전특구 시범지역 1유형’ 도전",
"산업단지 수요, 각종 개발호재…천안역 경남아너스빌 어반하이츠 관심",
"국힘 박성호 김해갑 예비후보 고부가 가치 4대 미래 전략산업 육성",
"국힘 박성호 예비후보 청년 연령 39→45세 상향 조정",
"영암군, '인구 희망 8대 프로젝트' 적극 행정 실천",
"익산시, 명품 교육도시 명성 되찾는다",
"중국도 저출생·고령화 속 '노인 돌봄'이 문제…간병인 부족",
"전남도, 올해 노인복지 예산 1조6000억 편성",
"[청론직설] 나눠먹기 정치로는 성장·발전 못해…‘달빛철도’ 등 나쁜 입법...",
"영암군, '인구 희망 8대 프로젝트' 7000억 투입",
"울산 노동인구 <b>감소</b> 대비 중장년 대상 재교육·취업지원 강화 절실",
"경남기후위기비상행동 총선 후보들 기후공약 마련하라",
"수영구 장예찬, 동방오거리역 신설 등 3대 공약 발표",
"'영암 인구 희망 8대 프로젝트'로 정주인구 6만, 생활인구 30만 유치",
"전남, 노인복지 예산 1조 6천억 다양한 시책 마련",
"익산으로 이사 갈래요 명품 교육도시 조성 박차",
"전남도, 노인복지 예산 1조6000억 편성…전년 대비 1000억 증액",
"소멸위험도시 태백…지난해 출생아, 도내 <b>감소</b>율 최고",
"거창군, 교육발전특구 시범지역 경남 최초 도전",
"[딜링룸 백브리핑] &quot;美 빅테크, 올해도 감원 이어갈 것&quot;",
"“제주올레 완주자 97.2%, 정신 건강 좋아져”",
"실업급여 신규 신청 ‘20만명’…20대 청년층 고용보험 가입 ‘뚝’, 왜?",
"전주 출신 이정헌 전 JTBC 뉴스앵커, 서울 광진갑 민주당 예비후보 출사표",
"전남도, 어르신이 행복하고 편안한 노후 최선",
"구인모 거창군수, 교육으로 인구 유입…교육특구신청서 제출",
"제주올레 완주자 10명 중 9명, 정신·사회·신체 '건강↑'",
"경남 환경단체 &quot;총선 출마 후보, 기후위기 대응 공약 마련해야&quot;",
"신재생에너지 연료자원으로 떠오른 수수줄기",
"수영구 장예찬, 동방오거리역 신설 등 수영 3대 공약 발표",
"익산으로 이사 갈래요 명품 교육도시 조성 박차",
"거창군, 교육발전특구 시범지역 1유형 경남도 내 최초 도전",
"영암군, ‘영암 인구 희망 8대 프로젝트’ 추진",
"직업? 필요 없어요 알바만 하는 '프리터족'",
"장예찬, 동방오거리 신설 등 ‘수영 1등 도시 도약’ 3대 공약 발표"]


def translate_list_elements(input_list, target_language='en'):
    translator = Translator()
    translation_result = []
    for element in input_list:
        translation = translator.translate(element, dest=target_language).text
        translation_result.append({element: translation})
    return translation_result


for i in data_list:
    translated_dict_list = translate_list_elements([i])
    total_list.append(translated_dict_list)
emotional_result = dict()
for i in total_list:
    if swn_polarity(list(i[0].values())[0]):
        emotional_result.setdefault(list(i[0].items())[0][0], "긍정")
    else:
        emotional_result.setdefault(list(i[0].items())[0][0], "부정")

df = pd.DataFrame(emotional_result.items(), columns=['title', 'result'])
print(df)
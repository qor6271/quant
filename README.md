# 폴더 설명
## 1. data_directory
## 2. backtest
## 3. strategy

------

# 1. data_directory

## 분석에 필요한 데이터 파일들 존재
    
    korea_corporation.csv : 한국 상장 기업 목록, 최신화 시점은 2021년 11월 언젠가, 출처는 한국거래소, http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201
    
    korea_etf.csv : 한국 etf 목록, 최신화 시점은 2021년 11월 언젠가, 출처는 한국거래소, http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201030104

    위의 데이터만 가지고 백테스팅 돌리면 생존편향 문제 생길 수 있음. 아래 kospi_200 데이터처럼 과거의 기업목록, etf목록도 있으면 좋을 것 같다.

    kospi_200_{year} : 해당 년도 1월 기준 kospi_200 기업 목록, 출처는 한국거래소, http://index.krx.co.kr/contents/MKD/03/0304/03040101/MKD03040101.jsp?idxCd=1028&upmidCd=0102#a110dc6b3a1678330158473e0d0ffbf0=3
    kospi_200 : kospi_200 기업 목록, 최신화 시점은 2021년 11월 언젠가, 출처는 한국 거래소(2022년 1월에 최신화 할 예정), 링크 위와 동일
    -> 파일 통합도 나쁘지 않을듯

    make_stock_price.ipynb, make_etf_price.ipynb : 네이버 금융에서 각각 주식가격, etf가격 크롤링 해오는 코드. 용량이 커 깃헙에 csv 파일을 못올림으로 알아서 크롤링해서 써야 할 듯, 크롤링 해올 시작날짜와 끝나는 날짜만 수정해서 사용하면 된다. 시간 30분정도 소요될듯?

    company_guide.csv : 한국 상장 기업들의 재무재표 및 투자지표, 출처는 company guide 사이트, 문제점 많음
    1. 크롤링 해올 수 있는 데이터가 약 3년 정도로 부족함. -> 다른 대안 사이트 찾아야 할 것 같음(일단 좋아보이는 것은 open dart api나 dart_fss 파이썬 라이브러리)
    2. 기업마다 재무제표를 올리는 날짜, 이름 등이 달라서 통일성 있는 데이터 만들기 어려움 -> 정규 표현식을 쓰던지 어떤 추가적인 처리 필요해보임
    3. 누락 데이터 많음(이건 기업이 안올린 거라 어쩔 수 없는듯)
    -> 아직 사용하지 않는다. 나중에 가치투자를 한다면 해결해야 할 과제 중 하나.
    
# 2. regular_backtesting(규칙적으로 리밸런싱하는 백테스팅 라이브러리)

## Backtest.py

### class regular_Backtest(price_df, strategy_class, seed_money = 10000000)

변수 설명

    price_df : 가격 데이터 프레임 입력, data_directory에 있는 make_stock_price.ipynb, make_etf_price.ipynb 에서 생성된 파일 판다스 데이터프레임 형식으로 읽어와 넣으면 된다. 주식 가격으로 테스트하고 싶으면 주식 가격, etf 가격으로 테스트하고 싶으면 etf 넣으면 된다.

    strategy_class : strategy 라이브러리에 있는 퀀트 전략 class를 넣으면 된다. 차후 다시 설명

    seed_money : 백테스팅 하는데 초기 자본, 기본값 = 10000000

백테스팅 방법

    backtest = BackTesting(price_df = stock_price, strategy_clsas = momentum)

    backtest.fit(start = '201301', end = '202101', rebal_month = 3)

    start : 백테스팅 시작 날짜, 년 월 단위까지 작성. '201301' -> 2013년 1월
    end : 백테스팅 끝나는 날짜, 마찬가지로 년 월 단위까지 작성
    rebal_month : 리밸런싱 기간. 단위는 월(month)이며 기본값은 None (리밸런싱 하지 않음) 

백테스팅 결과

    backtest.balance : 백테스트 한 결과 통장을 판다스 데이터프레임 형태로 보여줌
    열에는 각각 개별주식(코드명), 종합 주식('stock'), 현금('cash'), 종합 잔고('total'), 수익률('rate_of_return'), 최대낙폭('MDD') 값
    행에는 날짜
    예: 수익률을 보고싶으면 backtest.balance['rate_of_return']

    backtest.CAGR : 백테스트 한 결과 CAGR 값을 월(month) 단위로 보여줌(첫 6개월은 변동성 심하므로 제외)

그밖의 함수

    fit()에 사용되는 함수로 궁금하면 알아서 뜯어보도록
    
    대략적인 설명

    backtest.fit() 실행 시 
    1. date_division 함수에서 시작 날짜와 끝 날짜 사이를 rebal_month에 맞게 날짜를 나눔
    2. strategy_class의 전략에 맞게 투자할 주식과 그 주식들의 비율을 전달받음
    3. 전달받은 데이터를 make_balance 함수에 넣어 다음 리밸런싱 전까지 투자내용들을 balance에 저장
    4. 2,3 과정을 rebal_month기준으로 끝날때까지 반복

## basic.py

### class ratio_adjustment(stocks, ratio)

설명

    투자하려는 주식들과 그 주식들의 투자비율을 조정하는 가장 기본적인 전략

변수 설명

    stocks : 주식 코드를 list형태로 입력
    ratio : stocks에 해당하는 주식들의 비율을 list형태로 입력 (합이 1이 되게)

ex : kodex200(A069500) etf와 tiger 국채3년(A114820) etf를 3개월마다 같은 비율로 리밸런싱해 8년간 백테스팅할 경우

    RA = ratio_adjustment(['A069500', 'A114820'], [1/2,1/2])
    backtest = BackTesting(price_df = etf_price, strategy_class = RA)
    backtest.fit(start = '201301', end = '202101', rebal_month = 3)

## momentum.py

### class relative_momentum(stocks, time_period = 12, fip_on = False, momentum_number = 50, fip_number = 20, last_month_in = True)

설명

    상대적 모멘텀 전략 : 주식이 오르는 경향이 있으면 그 경향을 유지하려는 성질을 가지고 있다(모멘텀)는 가정하에 만들어진 전략으로, 과거에 수익률이 높은 주식일수록 앞으로의 수익률도 높을것이라고 판단해 수익률이 높은 주식들을 매수

변수 설명

    stocks : 수익률을 계산해 볼 주식들 코드를 list형태로 입력, 이 주식들 중 수익률이 높은 주식들을 선택해 투자하게 된다.
    time_period : 과거의 수익률을 계산해 보는 기간을 말함, 단위는 달(month), 기본값은 12
    예를 들어 과거 6개월 동안 수익률이 높았던 주식들에 투자하고 싶으면 time_period = 6으로 설정
    momentum_number : 계산한 수익률을 높은 순서대로 몇개를 고를 것인지, 기본값은 50
    예를 들어 수익률이 높은 순서대로 20개의 주식에 투자하고 싶으면 momentum_number = 20 으로 설정

    ---- 여기부터는 별로 쓸모 없을듯, 수익률을 올리려는 지표로 사용하려 했으나 백테스팅 결과 효과가 나타나지 않음 ---
    fip_on : fip은 과거 수익률에서 얻을 수 있는 지표 중 하나로 (과거의 수익률의 부호) * (주식이 오른 날의 숫자 - 주식이 떨어진 날의 숫자) 로 계산
    fip 값이 낮을수록 앞으로 모멘텀을 유지할 가능성이 높다고 함. fip 지표를 사용할지 여부(True, False), 기본값은 False
    fip_number : fip_on = True 일 경우 fip 값이 낮은 순서대로 몇개를 고를 것인지, 기본값은 20. momentum_number로 추려진 주식들을 대상으로 fip을 계산해 최종 투자할 종목들을 정한다.
    last_month_in : 과거의 수익률을 계산할 때 마지막 한달(제일 최근 달)을 포함할지 여부. 마지막 달을 포함을 시키지 않는게 데이터에 더 안정적이라는 말이 있다(책에 의하면). 값은 True, False, 기본값은 True

ex : 코스피200 기업들을 대상으로 지난 12월간 수익률이 높았던 기업들 20개에 투자하며, 3개월마다 리밸런싱할 때 8년간 백테스팅할 경우

    RM = relative_momentum(stocks = kospi_200['종목코드'], momentum_number = 20)
    backtest = BackTesting(price_df = stock_price, strategy_class = RM)
    backtest.fit(start = '201301', end = '202101', rebal_month = 3)


### class relative_momentum_test(stocks, time_period = 12, section_cut = 5, rank = 1, last_month_in = True):

설명

    상대적 모멘텀 전략이 유효한지 테스트하기 위한 클래스로 과거의 수익률을 상위부터 하위까지 분위별로 나누어 각각의 분위들의 수익률을 확인하기 위한 목적.
    상위 분위가 수익률이 잘 나올수록 상대적 모멘텀이 효과가 있다는 것을 입증

변수 설명

    relative_momentum 과 변수가 비슷하며 다른 변수들만 설명
    section_cut : 과거의 수익률을 순서대로 몇분위로 나눌지, 기본값은 5
    rank : 나눈 분위수 중 몇번째 분위의 주식들을 선택할 것인지, 값은 1부터 section_cut까지, 기본값은 1

ex : 코스피200 기업들을 대상으로 지난 12월간 수익률이 상위 20~40퍼센트(5분위수로 나눴을 때 2분위)였던 기업에 투자하며, 3개월마다 리밸런싱할 때 8년간 백테스팅할 경우
    
    RM = relative_momentum_test(stocks = kospi_200['종목코드'], rank = 2)
    backtest = BackTesting(price_df = stock_price, strategy_class = RM)
    backtest.fit(start = '201301', end = '202101', rebal_month = 3)
    

### dual_momentum(min_rate_of_return = 0.02, time_period = 12, stocks = ['A143850','A195930','A101280','A069500']):
    
설명

    듀얼 모멘텀 전략 : 상대적 모멘텀과 절대적 모멘텀을 합친 것, 상대적 모멘텀이 수익률이 높은 기업들을 판단한다면, 절대적 모멘텀은 일정 수익률을 기준으로 그 수익률보다 높으면 매수, 낮으면 매도. 듀얼모멘텀은 상대적모멘텀을 통해 수익률이 높았던 주식들을 찾은 뒤 절대적 모멘텀을 기준으로 주식을 매수할지 매도할지 판단.

변수 설명

    stocks : 수익률을 계산해 볼 주식들 코드를 list형태로 입력. 기본값은 순서대로 미국s&p500 etf, 유로스탁스50 etf, 일본topix100 etf, kodex200 etf
    time_period : 과거의 수익률을 계산해볼 기간, 단위는 달(month), 기본값은 12
    min_rate_of_return : 과거의 수익률을 판단하는 기준으로 기준보다 높으면 매수, 낮으면 현금보유(사지 않는다), 기본값은 0.02

    relative_momentum과 다르게 매수할 주식 개수는 따로 정하지 않으며 과거 수익률이 가장 높은 주식 하나만 선택. 그 주식이 min_rate_of_return보다 높으면 매수, 낮으면 현금보유

    좀 더 일반화가 필요해보인다.

ex : 4개 etf(기본값)를 대상으로 지난 12월간 수익률이 가장 높은 etf를 찾은 뒤 그 수익률이 min_rate_of_return보다 크면 매수, 낮으면 현금보유, 3개월마다 리밸런싱할 때 8년간 백테스팅할 경우
    
    DM = dual_momentum_test()
    backtest = BackTesting(price_df = stock_price, strategy_class = DM)
    backtest.fit(start = '201301', end = '202101', rebal_month = 3)
  


## value.py

    가치투자를 위해 만든 라이브러리지만, 재무제표가 불완전한 관계로 보류


# 3. irregular_backtesting(불규칙적으로 리밸런싱하는 백테스팅 라이브러리)

## Backtest.py

수정예정


------
그밖에 파일들은 내가 여러가지 테스트 해본 것들이니 알아서 보도록 bollinger_test, ema130_test는 볼린저 밴드, 이동평균선 공부하면서 끄적인거 나중에 라이브러리로 개발 예정

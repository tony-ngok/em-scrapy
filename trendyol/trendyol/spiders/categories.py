import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl trendyol_categorie
class TrendyolCategorie(scrapy.Spider):
    name = 'trendyol_categorie'
    allowed_domains = ['www.trendyol.com']
    start_urls = ['https://www.trendyol.com/kozmetik-x-c89']
    cats_output = "trendyol_categories.txt"

    COOKIES = {
        "FirstSession": "0",
        "ForceUpdateSearchAbDecider": "forced",
        "OptanonAlertBoxClosed": "2024-11-11T16:04:45.521Z",
        "OptanonConsent": "isGpcEnabled=0&datestamp=Mon+Nov+11+2024+10%3A04%3A50+GMT-0600+(hora+est%C3%A1ndar+central)&version=6.30.0&isIABGlobal=false&hosts=&genVendors=V77%3A0%2CV67%3A0%2CV79%3A0%2CV71%3A0%2CV69%3A0%2CV7%3A0%2CV5%3A0%2CV9%3A0%2CV1%3A0%2CV70%3A0%2CV3%3A0%2CV68%3A0%2CV78%3A0%2CV17%3A0%2CV76%3A0%2CV80%3A0%2CV16%3A0%2CV72%3A0%2CV10%3A0%2CV40%3A0%2C&consentId=bb0f89e6-3e05-476e-bea1-f2a2e4d4ab88&interactionCount=1&landingPath=NotLandingPage&groups=C0002%3A1%2CC0004%3A1%2CC0003%3A1%2CC0001%3A1%2CC0007%3A1%2CC0009%3A1&geolocation=TR%3B06&AwaitingReconsent=false",
        "SearchMode": "1",
        "VisitCount": "1",
        "WebAbTesting": "A_14-B_46-C_100-D_15-E_93-F_27-G_21-H_13-I_85-J_97-K_55-L_85-M_49-N_16-O_80-P_96-Q_12-R_43-S_70-T_100-U_85-V_47-W_71-X_49-Y_71-Z_45",
        "WebRecoAbDecider": "ABcrossRecoVersion_1-ABcrossRecoAdsVersion_1-ABsimilarRecoAdsVersion_1-ABsimilarSameBrandVersion_1-ABattributeRecoVersion_1-ABbasketRecoVersion_1-ABcollectionRecoVersion_1-ABshopTheLookVersion_1-ABcrossSameBrandVersion_1-ABcompleteTheLookVersion_1-ABsimilarRecoVersion_1-ABpdpGatewayVersion_1-ABhomepageVersion_firstComponent%3AinitialNewTest_1.performanceSorting%3AwidgetPerformanceFreqV1_3.sorter%3AhomepageSorterNewTest_d%28M%29-ABnavigationSideMenuVersion_sideMenu%3AinitialTest_1%28M%29-ABnavigationSectionVersion_section%3AazSectionTest_1%28M%29",
        "__cf_bm": "phfrOpULWrqS.QC1d0PEvPmXBBI7AClvBkKJDTmQTfs-1731341078-1.0.1.1-8GVC3XMsmmGdi0oLj.bx9RMKQRnvtC4vGvNExTf_Ev0YqKCr9y.92co24deWkcEpXO7Pd3cI6IBl8.xhptgmCw",
        "_cfuvid": "vnnSDSct1UUsdrnhOJ3rEs24JjGNGPondl95HNInMH4-1731341078622-0.0.1.1-604800000",
        "_fbp": "fb.1.1731341089980.416062928773427444",
        "_gcl_au": "1.1.81461011.1731341088",
        "_ym_d": "1731341092",
        "_ym_isad": "2",
        "_ym_uid": "1731341092939299798",
        "hvtb": "1",
        "msearchAb": "ABSearchFETestV1_A-ABSuggestionLC_B-ABSuggestionPS_A",
        "pid": "5150f76a-af49-4b83-9795-9a47243bdfae",
        "platform": "web",
        "recoAb": "ABRecoBETestV1_B-ABRecoFirstTest_A",
        "sid": "Ux7FkHQJOe"
    }

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Priority": "u=0, i",
        "Referer": "https://www.trendyol.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False

    def get_cat(self, url: str):
        if '?' in url:
            url = url.split('?')[0]
        return url.split('/')[-1]

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.HEADERS, cookies=self.COOKIES,
                             meta={ 'cookiejar': 0 },
                             callback=self.parse)

    def parse(self, response: HtmlResponse):
        subcats = response.css('div.ctgry div[role="rowgroup"] a')
        hrefs = [sc.css('::attr(href)').get() for sc in subcats]
        subcats_links = ['https://www.trendyol.com'+href for href in hrefs if href != '/sr']

        if not subcats_links:
            cat = self.get_cat(response.url)
            self.write_cat(cat)
        else:
            for sl in subcats_links:
                headers = { **self.HEADERS, 'Referer': response.url }
                yield scrapy.Request(sl, headers=headers,
                                     meta={ 'cookiejar': response.meta['cookiejar'] },
                                     callback=self.parse)

    def write_cat(self, cat: str):
        mod = 'a' if self.retry else 'w'
        with open(self.cats_output, mod, encoding='utf-8') as f_cats:
            f_cats.write(cat+'\n')
        if not self.retry:
            self.retry = True

import scrapy
import requests
import re

# primeiro crawler do projeto buscabike
# scrapy shell 'https://www.darien.com.br/bicicleta-aro-29-tsw-rava-pressure-27-pretovermvioleta' -s USER_AGENT='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
# scrapy runspider crawler_darien.py -o quotes.csv

class CrawlerDarien(scrapy.Spider):
    name = 'Crawler_Darien'
    start_urls = ['https://www.darien.com.br/']

    def parse(self, response):
        link = response.xpath("//div[@class='conteiner']//div//ul//li//a[@href='https://www.darien.com.br/bicicletas']/@href").get()
        
        yield scrapy.Request(
            link,
            callback = self.parse_bike
        )
    
    def parse_bike(self, response):
        bikes = response.css('a.produto-sobrepor::attr(href)').getall()

        for bike_url in bikes:
            yield scrapy.Request(
                bike_url,
                callback = self.parse_bike_detail
            )
        
        pages_url = response.css('.pagination a::attr(href)').getall()
        for page in pages_url:
            yield scrapy.Request(
                response.urljoin(page),
                callback = self.parse_bike
            )
    
    def parse_bike_detail(self, response):
        marca = response.css('div.info-principal-produto span a::text').get()
        modelo = response.css('div.info-principal-produto h1::text').get()
        preco_parcelado = ' '.join(response.css('strong.preco-promocional::text').get().split())
        preco_parcelado = preco_parcelado.split(' ')[1].replace('.','').replace(',','.')
        preco_avista = response.css('span.desconto-a-vista strong::text').get()
        preco_avista = preco_avista.split(' ')[1].replace('.','').replace(',','.')
        parcelas = response.css('span.preco-parcela strong::text').get()
        valor_parcela = round(float(preco_parcelado) / int(re.sub('[^0-9]', '', parcelas)),2)

        yield{
            'marca': marca,
            'modelo': modelo,
            'preco_parcelado': preco_parcelado,
            'preco_avista': preco_avista,
            'parcelas': parcelas,
            'valor_parcela': valor_parcela,
            'url': response.url
        }
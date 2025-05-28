# Integrantes

Bruno Giannini Loffreda | RA: 21.00122-7
Breno Amorim Roman      | RA: 20.00395-0

# Contextualização

O projeto está inserido no contexto da Internet das Coisas (IoT) e da Agricultura de Precisão. Deseja-se criar um módulo capaz de adquirir dados relevantes para agricultores como umidade do solo, pH do solo, velocidade do vento e temperatura. Para ser acessível ao público, pretende-se usar módulos acessíveis e baratos. O módulo deverá ser embarcado em um invólucro impresso em 3D a fim de protegê-lo do ambiente. O dispositivo deverá ser capaz de coletar dados dos sensores, armazená-los em um dispositivo interno, construindo uma série temporal.

# Requisitos

> RF - Requisito Funcional | RA - Requisito Adicional (melhorias futuras)

RF1
Ser composto de módulos de baixo custo e fácil acesso

RF2
Realizar a leitura do sensor de temperatura

RF3
Realizar a leitura do sensor de umidade

RF4
Ter um feedback visual do status do sistema

RF5
Realizar a leitura do RTC.

RF6
Encapsular as leituras dos sensores e do RTC em uma estrutura de dados.

RF7
Armazenar a estrutura de dados em uma memória interna

RF8
Ter uma bateria para permitir implantação em campo

R9
Construir um invólucro de proteção para os sensores

RA1
Implementar um sensor de direção do vento

RA2
Implementar um sensor de velocidade do vento

RA3
Implementar um sensor de nutrientes NPK

# Tecnologias Utilizadas

A fim de prover nossos usuários com as informações necessárias e relevantes, será utilizado um microcontrolador Raspberry Pi Pico modelo RP2040 para realizar a leitura dos sensores e a gravação no cartão SD. Entre os sensores figuram diferentes tipos de protocolos de comunicação, como Inter-Integrated Circuit (I2C, no módulo de cartão SD), Serial Peripheral Interface (SPI, no RTC) e Single-Wire Two-Way (no sensor de temperatura DHT11). A identificação destes parâmetros foi feita a partir do contato com a especificação técnica (datasheet) de cada componente. Além disso, o código fonte será desenvolvido utilizando micropython, utilizando a interface de programação Thonny Python para de fato gravar o firmware da aplicação no Raspberry Pi Pico.

# Componentes utilizados e preço estimado

* Sensor de temperatura DHT 11 

Preço: R$ 7,30 
Fonte: https://www.makerhero.com/produto/sensor-de-umidade-e-temperatura-dht11/?srsltid=AfmBOopsFJ1x9aUjLu8_uBrHiws60undxP7zAS17HPIrc8rxCod1hS0f 
		
* Sensor de luminosidade LDR 

Preço: R$ 1,50 
Fonte: https://www.makerhero.com/produto/sensor-de-luminosidade-ldr-5mm/
		
* Higromêtro 9SS19 

Preço: R$ 7,40 
Fonte: https://www.makerhero.com/produto/sensor-de-umidade-do-solo-higrometro/?srsltid=AfmBOoqyYzzcyfL3o7YHXyy9fap8N-cBBSmev7COTPIGiLXkuSpTpt2u
		
* Tiny RTC DS1307

Preço: R$ 11 
Fonte: https://www.casadarobotica.com/sensores-modulos/modulos/timers/modulo-relogio-rtc-ds1307-com-at24c32-i2c-e-bateria?parceiro=3259&srsltid=AfmBOoo24hLRC88BP4nO_ZpVH-UPhgBdOl2x4idtzHhF9ch758iE2rk-Up4
		
* Raspberry Pi Pico 

Preço: R$ 32 
Fonte: https://produto.mercadolivre.com.br/MLB-3112314420-placa-raspberry-pi-pico-_JM?matt_tool=18956390&utm_source=google_shopping&utm_medium=organic
		
* Módulo de Cartão SD

Preço: R$ 8,45 
Fonte: https://www.makerhero.com/produto/modulo-cartao-micro-sd/?srsltid=AfmBOooByDuJjfuCW8lfrf0OjAnchOa4hVjcVNV4jDAXFf5g9o6SZU5m
				
* Baterias 3,7V 

Preço: R$ 37,5 
Fonte: https://www.lojafornecedormundial.com.br/componentes-eletronicos/pilhas-e-celulas/10-pecas-bateria-3-7v-2100mah-7-77wh-litio-recarregavel-6sp753868
		
* Led Verde e Vermelho

Preço: R$ 0,2 
Fonte: https://www.casadarobotica.com/componentes-eletronicos/led-s/alto-brilho/1000x-led-vermelho-de-3mm-alto-brilho?parceiro=3259&srsltid=AfmBOor6tIfHC0zWL28n4vTretZTyDfgVmHgYg7AGRM7srE_-UIxOOQj54I
		
* Botão 

Preço: R$ 0,4 
Fonte: https://www.casadarobotica.com/componentes-eletronicos/partes/chaves-e-botoes/10x-mini-chave-tactil-push-button-botao-6x6x4-5mm

# Descrição breve das funções desenvolvidas:

* read_dht_ext(): lê a temperatura e umidade a partir do DHT 

* read_higrom(): lê o sensor de umidade do solo

* read_ldr(): lê a tensão no pino do LDR e retorna um valor em porcentagem para a luminosidade

* initialize_rtc(): define a data inicial do RTC, marcando o início da série temporal. 

* read_rtc(): lê um valor de tempo definido pelo RTC 

* get_readings(): chama as funções de leitura dos sensores durante `N_READINGS` segundos e calcula as médias para serem armazenadas

* sd_setup(): configura o cartão SD verificando a existência do arquivo "readings.csv". Cria o arquivo caso ele não exista e insere o cabeçalho do arquivo 

* write_payload(): gera a payload concatenando os valores dasleituras com o timestamp e grava no cartão SD

* check_status(): realiza um ciclo teste de leituras dando feedback com os leds. Acionado via uma interrupção gerada por um botão.

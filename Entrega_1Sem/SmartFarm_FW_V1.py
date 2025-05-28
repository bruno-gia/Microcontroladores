##########################################################################
#                                                                        #
#              ** FW - MauaSmartFarm V1.0 - 28/04/2025 **                #
#                                                                        #
# A seguir serão especificadas as principais funções a serem implemneta- #
# das nesta versão do firmware:                                          #
#                                                                        #
#	* read_dht_ext(): lê a temperatura e umidade a partir do DHT         #
#                                                                        #
#	* read_higrom(): lê o sensor de umidade do solo                      #
#                                                                        #
#	* read_ldr(): lê a tensão no pino do LDR e retorna um valor em       #
#				  porcentagem para a luminosidade                        #
#                                                                        #
#	* initialize_rtc(): define a data inicial do RTC, marcando o início  #
#                       da série temporal.                               #
#                                                                        #
#	* read_rtc(): lê um valor de tempo definido pelo RTC                 #
#                                                                        #
#	* get_readings(): chama as funções de leitura dos sensores durante   #
#					  N_READINGS segundos e calcula as médias para serem #
#                     armazenadas                                        #                                                                      #
#                                                                        #
#	* sd_setup(): configura o cartão SD verificando a existencia do      #
#				  arquivo "readings.csv". Cria o arquivo caso ele não    #
#				  exista e insere o cabeçalho do arquivo                 #
#                                                                        #
#	* write_payload(): gera a payload concatenando os valores das        #
#                      leituras com o timestamp e grava no cartão SD     #   
#                                                                        #                                                                       #                                                #
#                                                                        #
#	* check_status(): realiza um ciclo teste de leituras dando feedback  #
#                     com os leds. Acionado via um interrupção gerada    #
#                     gerada por um botão.                               #
# ---------------------------------------------------------------------- #
#                     === Pinagem - Sensores -> Pico ===                 #
#                                                                        #
# * DHT11:                                                               #
# 	DATA -> GP15                                                         #
#                                                                        #
# * Higrometro -> GP27_A1                                                #
#                                                                        #
# * LDR -> GP26_A0                                                       #
#                                                                        #
# * LED Vermelho -> GP10                                                 #
#                                                                        #
# * LED Verde -> GP11                                                    #
#                                                                        #
# * RTC:                                                                 #
#	SDA -> GP0                                                           #
#	SCL -> GP1                                                           #
#                                                                        #
# * Módulo SD:                                                           #
#	MISO -> GP4                                                          #
#	MOSI -> GP3                                                          #
#	SCK  -> GP2                                                          #
#	CS   -> GP5                                                          #
#                                                                        #
# * Botão:                                                               #
#	GP14                                                                 #
#                                                                        #
##########################################################################

# Importação das bibliotecas:
import sys
sys.path.append('/libs')

from libs.ds1307 import DS1307
from sdcard import SDCard

from machine import Pin, ADC, I2C, RTC
import dht
import time
import os 

# Definição dos sensores nos pinos especificados:

dht_ext = dht.DHT11(Pin(15, Pin.IN, Pin.PULL_UP))
ldr = ADC(Pin(26))
higrom = ADC(Pin(27))
green_led = Pin(10, Pin.OUT)    
red_led = Pin(11, Pin.OUT)

# Interface SPI para o módulo SD
spi = machine.SPI(0,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4)) 

# Inicialização da interface I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1))  
rtc = DS1307(i2c)

# Inicialização do módulo SD
sd = SDCard(spi, machine.Pin(5))   

# Definição do Botão para interrupções
check_status_btn = Pin(14, Pin.IN, Pin.PULL_UP)

#------------------ Definição das funções ---------------------

def read_dht_ext():
    try:
        # Inicia a leitura
        dht_ext.measure()
        
        # Extrai os valores:
        ext_temp = dht_ext.temperature()
        ext_hum = dht_ext.humidity()
        
        # Debug no terminal:
        print(f"** Leitura de Temperatura do DHT11: **")
        print(f"** Temperatura: {ext_temp}°C || Umidade: {ext_hum} %**")
        
        return [ext_temp, ext_hum]
        
    except Exception as e:
        print(f"Erro ao ler DHT11: {e}")
        return [0,0]

def read_higrom():
    
    """
    Realiza a leitura do Higrômetro externo, retornando o valor de humidade do solo.
    
    Parâmetros usados para a calibração:
    
        * Tensão solo encharcado:
        
        * Tensão solo seco:
    """
    
    print("\n----------------------------")
    print("Chamou a função read_higrom()\n")
    
    try:
        
        # Extração do valor da entrada analógica como número de 16 bits (de 0 a 65535)
        higrom_analog_value = higrom.read_u16()
        
        # Conversão para um valor de tensão entre 0 e 3.3 V
        higrom_voltage = (higrom_analog_value/65535) * 3.3
        
        # Normalização para um valor em porcentagem:
        higrom_hum = (higrom_analog_value/65535) * 100
        
        # Debug Feeback:
        print(f"** Leitura do Higromêtro: **")
        print(f"** Valor analógico: {higrom_analog_value}  ||  Tensão: {higrom_voltage:.2f} V  ||  Umidade: {higrom_hum:.1f}% **")
        
        return higrom_hum
        
    except Exception as e:
        print(f"Erro na leitura do higrômetro: {e}")
        return 0
       
    print("\n----------------------------")
    

def read_ldr():
    
    """
    Realiza a leitura do LDR, retornando o valor de luminosidade.
    
    Parâmetros usados para a calibração:
    
        * Tensão Escuro:
        
        * Tensão Claro:
    """
    
    print("\n----------------------------")
    print("Chamou a função read_ldr()\n")
    
    try:
        
        # Extração do valor da entrada analógica como número de 16 bits (de 0 a 65535)
        ldr_analog_value = ldr.read_u16()
        
        # Conversão para um valor de tensão entre 0 e 3.3 V
        ldr_voltage = (ldr_analog_value/65535) * 3.3
        
        # Normalização para um valor em porcentagem:
        lum = (ldr_analog_value/65535) * 100
        
        # Debug Feeback:
        print(f"** Leitura do LDR: **")
        print(f"** Valor analógico: {ldr_analog_value}  ||  Tensão: {ldr_voltage:.2f} V  ||  Luminosidade: {lum:.1f}% **")
        
        return lum
        
    except Exception as e:
        print(f"Erro na leitura do LDR: {e}")
        return 0
       
    print("\n----------------------------")

def initialize_rtc(year, month, day, hour, minute, second):
    
    """
    Inicializa o RTC em uma data pré definida.
    
    """
    try:
        
        # Definição da data inicial
        start_date = (year, month, day, 0, hour, minute, second, 0)
        rtc.datetime(start_date)
        
        print(f"RTC ajustado para: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
        return True
    
    except Exception as e:
        print(f"Falha ao ajustar RTC: {e}")
        return False
    
def read_rtc():
    
    """
    Realiza a leitura do RTC, extraindo um Timestamp a sre adicionado à payload gerada a partir dos dados coletados.
    """
    
    print("\n----------------------------")
    print("Chamou a função read_rtc()")
    
    try:
        
        # Extração da data:
        timestamp = rtc.datetime()
        print(timestamp)
        
        # Formatação para string
        formatted_timestamp = f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[4]:02d}:{timestamp[5]:02d}:{timestamp[6]:02d}"
        print(formatted_timestamp)
        return formatted_timestamp
    
        

    except Exception as e:
        
        print(f"Erro na leitura do RTC: {e}")
        return 0

    print("\n----------------------------")

def get_readings():
    
    """
    Realiza a leitura de todos os sensores durante N_READINGS s a partir da chamada das funções de leitura individuais.
    Calcula a média das leituras realizadas
    """
    
    print("\n----------------------------")
    print("Chamou a função get_readings()\n")
    
    # Definição do número de leituras a serem realizadas por ciclo:
    N_READINGS = 5
    
    # Inicialização dos acumuladores para cada variável:
    dht_temp_acc = 0
    dht_hum_acc = 0
    higrom_hum_acc = 0
    lum_acc = 0
    
    for i in range(N_READINGS):
        
        # Lê o DHT
        dht_readings = read_dht_ext()
        
        dht_temp = dht_readings[0]
        dht_hum = dht_readings[1]
        
        if dht_temp != 0:
            dht_temp_acc = dht_temp_acc + dht_temp
            
        if dht_hum != 0:
            dht_hum_acc = dht_hum_acc + dht_hum

            
        # Lê a humidade do higrômetro:
        higrom_hum = read_higrom()
        
        if higrom_hum != 0:
            higrom_hum_acc = higrom_hum_acc + higrom_hum
            
        # Lê a luminosidade do LDR:
        lum = read_ldr()
        
        if lum != 0:
            lum_acc = lum_acc + lum
        
        # Intervalo de 1s entre as leituras
        time.sleep(1)
        
    # Calcula as médias
    dht_temp_mean = dht_temp_acc / N_READINGS 
    dht_hum_mean = dht_hum_acc / N_READINGS
    higrom_hum_mean = higrom_hum_acc / N_READINGS
    lum_mean = lum_acc / N_READINGS
    
    # Armazena as médias em um Vetor
    readings_mean = [dht_temp_mean, dht_hum_mean, higrom_hum_mean, lum_mean]
    
    print("Término do ciclo de leituras...")
    print(readings_mean)
    print("\n----------------------------")
    
    return readings_mean

def sd_setup():
    
    """
    Inicializa o módulo de cartão SD. Verifica a existência do arquivo "readings.csv" e cria-o se não existir.
    """
    print("\n----------------------------")
    print("Chamou a função sd_setup\n")
     
    try:
        # Montagem do sistema de arquivos
        os.mount(sd, '/sd')
        print("Cartão montado em '/sd'")
        
        # Verifica/cria o arquivo readings.csv
        if 'readings.csv' not in os.listdir('/sd'):
            with open('/sd/readings.csv', 'w') as f:
                f.write("TIMESTAMP;TEMP;HUM_EXT;HUM_HIG;LUM\n")
            print("Arquivo *readings.csv* criado! Cabeçalho inserido!")
        else:
            print("Setup já realizado! Seguindo...")
            
        return True
        
    except Exception as e:
        print(f"[SD] Erro: {e}")
        return False
    
    print("\n----------------------------")
  
def write_payload(timestamp, readings_mean):
    
    """
    Concatena as informações retiradas dos sensores e grava a payload gerada no cartão SD, identificada pelo Timestamp
    retirado do RTC.
    """
    print("\n----------------------------")
    print("Chamou a função write_payload()\n")
    
    # Construção da string no formato esperado:
    payload = f"{timestamp};{readings_mean[0]:.1f};{readings_mean[1]:.1f};{readings_mean[2]:.1f};{readings_mean[3]:.1f}\n"

    # Escrita no cartão sd:
    with open('/sd/readings.csv', 'a') as file:
        file.write(payload)
    
    print("\n----------------------------")

def check_status(pin):
  
    """
    Entra em um ciclo de verificação para as leituras dos sensores ao ser apertado um botão.
    Realiza um ciclo de leituras, acionando os leds de acordo com o resultado.
    
    1 - Ambos os leds ficam acesos por 2 s
    2 - Teste DHT (1 piscada do led verde)
    3 - Teste do Higrometro (2 piscadas do Led verde)
    4 - Teste do LDR (3 piscadas do Led verde)
    
    A cada leitura, apresenta-se o feedback:
    
    3 piscadas rápidas do Led Verde -> Ok
    3 piscadas rápidas do Led Vermelho -> Erro
    """
    
    print("\n----------------------------")
    print("--- INTERROMPIDO --- \nChamou a função check_status()\n")
    
    # Definição do número de leituras a serem realizadas por ciclo:
    N_READINGS = 1
    
    # Indica o início do teste
    green_led.toggle()
    red_led.toggle()
    time.sleep(3)
    green_led.toggle()
    red_led.toggle()
    time.sleep(1)
    
    for i in range(N_READINGS):
        
        # Marca a leitura do DHT
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        
        dht_readings = read_dht_ext()
        
        dht_temp = dht_readings[0]
        dht_hum = dht_readings[1]
        
        if (dht_temp + dht_hum) == 0:
            # Erro
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
        
        else:
            # Sucesso
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            
        # Intervalo de 1s entre as leituras do DHT
        time.sleep(1)
        
        # Marca a leitura do Higrometro
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
            
        # Lê a humidade do higrômetro:
        higrom_hum = read_higrom()
        
        if higrom_hum == 0:
            # Erro
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
        
        else:
            # Sucesso
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            
        # Marca a leitura do LDR:
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()
        time.sleep(1)
        green_led.toggle()

            
        # Lê a luminosidade do LDR:
        lum = read_ldr()
        
        if lum == 0:
            # Erro
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
            time.sleep(0.4)
            red_led.toggle()
        
        else:
            # Sucesso
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
            time.sleep(0.4)
            green_led.toggle()
        
        # Marcação do fim
        green_led.toggle()
        red_led.toggle()
        time.sleep(3)
        green_led.toggle()
        red_led.toggle()
    
    
# Handler para a interrupção
check_status_btn.irq(trigger=Pin.IRQ_FALLING, handler=check_status)

#------------------ Setup - Comentar após a 1ª execução -------------------

#initialize_rtc(2025,5,14,18,50,0)

# --------------------------------- Loop Principal --------------------

sd_setup()

readings = get_readings()

timestamp = read_rtc()

write_payload(timestamp, readings)

get_readings()












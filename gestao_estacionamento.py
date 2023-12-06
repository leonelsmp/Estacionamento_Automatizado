from customtkinter import *
from requests import get
import pandas as pd
from datetime import date, timedelta 
from numpy import round
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from PIL import Image

class Dados():

    def __init__(self):
        response = get("http://leonelsmp.pythonanywhere.com/Historico")
        historico = pd.DataFrame( response.json())
        historico["DataFim"] = pd.to_datetime(historico["DataFim"])
        historico["DataInicio"] = pd.to_datetime(historico["DataInicio"])
        historico["Minutos"] = (historico["DataFim"] - historico["DataInicio"])/pd.Timedelta(15 ,"m")
        response = get("http://leonelsmp.pythonanywhere.com/Vagas")
        vagas = pd.DataFrame( response.json())

        self.vagas = vagas
        self.historico = historico
        self.tarifa = 5
        self.receita = round(self.Calcular_receita_diaria(),2)

    def Atualizar(self):
        response = get("http://leonelsmp.pythonanywhere.com/Historico")
        historico = pd.DataFrame( response.json())
        historico["DataFim"] = pd.to_datetime(historico["DataFim"])
        historico["DataInicio"] = pd.to_datetime(historico["DataInicio"])
        historico["Minutos"] = (historico["DataFim"] - historico["DataInicio"])/pd.Timedelta(15 ,"m")
        self.historico = historico
        response = get("http://leonelsmp.pythonanywhere.com/Vagas")
        self.vagas = pd.DataFrame( response.json())
        self.receita = round(self.Calcular_receita_diaria(),2)

        vagas_ocupadas.configure(text = self.Get_vagas_ocupadas())
        vagas_livres.configure(text = self.Get_vagas_livres())
        label_combox.configure(text = "Receita em R$: "  + str(self.receita))
        tempo.configure(text = self.Get_tempo_medio_diario())

    def Get_vagas_ocupadas(self):
        return "  Vagas Ocupadas: "+ str(self.vagas[self.vagas["Ocupada"] == True].shape[0])
    
    def Get_vagas_livres(self):
        return "  Vagas Livres: "+ str(self.vagas[self.vagas["Ocupada"] == False].shape[0])

    def Get_tempo_medio_diario(self):
        filtrar = self.historico[self.historico["DataInicio"] >= pd.to_datetime(date.today()) ]
        minutos = (filtrar["DataFim"] - filtrar["DataInicio"])/pd.Timedelta(1 ,"m")
        return "Tempo medio diario (minutos): "+ str(round(minutos.mean(), 3))

    def PUT_tarinfa(self):
        print(self.tarifa)
        try:
            self.tarifa = float(tarifa.get())
        except:
            self.data = 5

    def Calcular_receita_semanal(self):
        today = date.today()
        week_prior = pd.to_datetime( today - timedelta(weeks=1) )
        filtered_historico = self.historico[(self.historico["DataInicio"] >= week_prior) & (self.historico["DataInicio"] < pd.to_datetime( today))]
        receita = filtered_historico["Minutos"].sum()*self.tarifa
        return receita
    
    def Calcular_receita_diaria(self):
        today = pd.to_datetime( date.today())
        filtered_historico = self.historico[self.historico["DataInicio"] >= today]
        receita = filtered_historico["Minutos"].sum()*self.tarifa
        return receita
    
    def Selecionar_receita(self, choice = None):
        global canvas1, canvas2
        if choice == "Diario":
            self.receita = round(self.Calcular_receita_diaria(), 2)
            label_combox.configure(text = "Receita em R$: "  + str(self.receita))

            plt.close("all")
            canvas1.get_tk_widget().destroy()
            canvas1 = FigureCanvasTkAgg(dados.Grafico_diario_fluxo(), master=lowerFrame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

            canvas2.get_tk_widget().destroy()
            canvas2 = FigureCanvasTkAgg(dados.Grafico_diario_receita(), master=lowerFrame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="right", fill="both", expand=True)

        else:
            self.receita = round(self.Calcular_receita_semanal(),2)
            label_combox.configure(text ="Receita em R$: "  + str(self.receita))

            plt.close("all")
            canvas1.get_tk_widget().destroy()
            canvas1 = FigureCanvasTkAgg(dados.Grafico_semanal_fluxo(), master=lowerFrame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

            canvas2.get_tk_widget().destroy()
            canvas2 = FigureCanvasTkAgg(dados.Grafico_semnal_receita(), master=lowerFrame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="right", fill="both", expand=True)


    def Grafico_diario_fluxo(self):
        #quantidade diaria
        filtrar = self.historico[self.historico["DataInicio"] >= pd.to_datetime(date.today()) ]
        fig1, ax1 = plt.subplots()
        ax1.set_title('Quantidade de caros diaria')
        ax1.hist(filtrar["DataInicio"].dt.strftime("%d/%m/%Y %H:00"), bins=24, rwidth=0.9, color=Cor_texto)
        ax1.set_xlabel('Horas')
        ax1.set_ylabel('Qunatidade')
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        return fig1

    def Grafico_semanal_fluxo(self):
        today = date.today()
        week_prior = pd.to_datetime( today - timedelta(weeks=1) )
        filtered_historico = self.historico[(self.historico["DataInicio"] >= week_prior) & (self.historico["DataInicio"] < pd.to_datetime( today))]
        fig2, ax2 = plt.subplots()
        ax2.set_title('Quantidade de caros semanal')
        ax2.hist(filtered_historico["DataInicio"].dt.strftime("%d/%m/%Y"), bins=7, color=Cor_texto)
        ax2.set_xlabel('Dias')
        ax2.set_ylabel('Qunatidade')
        return fig2
    
    def Grafico_diario_receita(self):
        filtrar = self.historico[self.historico["DataInicio"] >= pd.to_datetime(date.today()) ]
        fig3, ax3 = plt.subplots()
        ax3.set_title('Receira diaria')
        ax3.bar(filtrar["DataInicio"].dt.strftime("%d/%m/%Y %H:00"), filtrar["Minutos"]*self.tarifa, color=Cor_texto)
        ax3.set_xlabel('Horas')
        ax3.set_ylabel('Receita (R$)')
        ax3.yaxis.set_major_locator(MaxNLocator(integer=True))
        return fig3
    
    def Grafico_semnal_receita(self):
        today = date.today()
        week_prior = pd.to_datetime( today - timedelta(weeks=1) )
        filtered_historico = self.historico[(self.historico["DataInicio"] >= week_prior) & (self.historico["DataInicio"] < pd.to_datetime( today))]
        fig4, ax4 = plt.subplots()
        ax4.set_title('Receita semanal')
        ax4.bar(filtered_historico["DataInicio"].dt.strftime("%d/%m/%Y"), filtered_historico["Minutos"]*self.tarifa, color=Cor_texto)
        ax4.set_xlabel('Dias')
        ax4.set_ylabel('Receita (R$)')
        return fig4


Cor_titulo ="#be29ec" 
Cor_texto = "#4158D0"
cor_fundo = "#84DCC6"
Cor_grafico = "#4158D0"
fonte = "PT Mono"
dados = Dados()



    
app = CTk()
app.geometry("1400x800")
set_appearance_mode("dark")
set_default_color_theme("dark-blue")
app.title("Gestão de Estacionamento")

###########################################################
upperFrame = CTkFrame(master=app)
upperFrame.pack(fill="both", expand=True, padx=10, pady=10, side="top", ipady=70)

###########################################################
LeftupperFrame = CTkFrame(master=upperFrame)
LeftupperFrame.pack(fill = "both" ,expand = True, padx = 10, side = "left")
CTkLabel(master=LeftupperFrame, text="Informações em Tempo Real", font=CTkFont(size=25, weight="bold"), justify="left", 
         text_color=Cor_titulo).pack(pady=(10, 10), side = "top")

imagem = CTkImage(Image.open("EV_car_Icon.png"), size=(26, 26))
vagas_ocupadas = CTkLabel(master=LeftupperFrame, text = dados.Get_vagas_ocupadas(), font=(fonte, 20), 
            justify="left", text_color=Cor_texto, corner_radius=32, image= imagem, compound="left" )
vagas_ocupadas.place(relx=0.3, rely=0.4, anchor=CENTER)

vagas_livres = CTkLabel(master=LeftupperFrame, text= dados.Get_vagas_livres(), font=(fonte, 20), 
            justify="left", text_color=Cor_texto ,corner_radius=32,  image= imagem, compound="left" )
vagas_livres.place(relx=0.3, rely=0.6, anchor=CENTER)

tempo = CTkLabel(master=LeftupperFrame, text= dados.Get_tempo_medio_diario(), font=(fonte, 20), 
            justify="left", text_color=Cor_texto, corner_radius=32 )
tempo.place(relx=0.3, rely=0.8, anchor=CENTER)

btn = CTkButton(master=LeftupperFrame, text="Atualizar", command = dados.Atualizar, corner_radius=32, fg_color="#4158D0", 
                hover_color="#C850C0", border_color="#FFCC70", 
                border_width=2)
btn.place(relx=0.8, rely=0.5, anchor=CENTER)

###########################################################
RightupperFrame = CTkFrame(master = upperFrame)
RightupperFrame.pack(fill = "both", expand = True, padx = 10, side = "right")
CTkLabel(master=RightupperFrame, text="Dados Financeiros", font=CTkFont(size=25, weight="bold"), justify="left", 
         text_color=Cor_titulo).pack(pady=(10, 10), side = "top")

CTkLabel(master=RightupperFrame, text="Preço em R$ por 15 minutos: ", font=(fonte, 20), justify="left", 
         text_color=Cor_texto).place(relx=0.3, rely=0.3, anchor=CENTER)
tarifa = CTkEntry(master=RightupperFrame, placeholder_text = str(dados.tarifa) ,font=(fonte, 20), justify="left", text_color=Cor_texto )
tarifa.place(relx=0.7, rely=0.3, anchor=CENTER)
CTkButton(master=RightupperFrame, text="Submeter", command = dados.PUT_tarinfa, corner_radius=32, fg_color="#4158D0", 
                hover_color="#C850C0", border_color="#FFCC70", 
                border_width=2).place(relx=0.5, rely=0.5, anchor=CENTER)


combox = CTkComboBox(master=RightupperFrame, values=["Diario", "Semanal"], font=(fonte, 20), justify="left", text_color=Cor_texto, command= dados.Selecionar_receita )
combox.place(relx=0.3, rely=0.68, anchor=CENTER)
label_combox  = CTkLabel(master=RightupperFrame, text= "Receita em R$: " + str(dados.receita), font=(fonte, 20), justify="left", 
         text_color=Cor_texto)
label_combox.place(relx=0.3, rely=0.88, anchor=CENTER)
###########################################################
lowerFrame = CTkFrame(master = app, bg_color = "#292929")
lowerFrame.pack(fill = "both", expand = True, padx = 10, pady = 10, side = "bottom")
CTkLabel(master=lowerFrame, text="Graficos", font=CTkFont(size=25, weight="bold"), justify="left", text_color=Cor_titulo).pack(pady=(10, 10), side = "top")

canvas1 = FigureCanvasTkAgg(dados.Grafico_diario_fluxo(), master=lowerFrame)
canvas1.draw()
canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

canvas2 = FigureCanvasTkAgg(dados.Grafico_diario_receita(), master=lowerFrame)
canvas2.draw()
canvas2.get_tk_widget().pack(side="right", fill="both", expand=True)

app.mainloop()

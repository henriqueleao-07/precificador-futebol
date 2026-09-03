import pandas as pd
import numpy as np
from numpy import random

ligas = {
    "1": ("Premier League", "E0"),
    "2": ("La Liga", "SP1"),
    "3": ("Bundesliga", "D1"),
    "4": ("Serie A", "I1"),
    "5": ("Ligue 1", "F1"),
    }
print("Escolha uma das 5 principais grandes ligas: ")
for chave, (nome, _) in ligas.items():
    print(f"[{chave}] {nome}")

escolha = input("\n Digite o nome da liga desejada: ")

if escolha not in ligas:
    print("[ERRO!] opção invalida, digite uma das ligas desejadas: ")
    exit()

nome_liga, codigo_liga = ligas[escolha]
print(f"\n Carregando dados da {nome_liga}...")

url = f"https://www.football-data.co.uk/mmz4281/2526/{codigo_liga}.csv"
dados_originais = pd.read_csv(url)

dados = dados_originais[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
dados = dados.rename(columns={'FTHG': 'GolsCasa', 'FTAG': 'GolsVisitante'})

times_disponiveis = sorted(dados['HomeTeam'].unique())
print("------------Analisador de Odds------------")
print('')
print("Times disponíveis na base de dados:")
print(", ".join(times_disponiveis))
print("-" * 50)

time_casa = input("Digite o nome do time da CASA: ")
time_fora = input("Digite o nome do time VISITANTE: ")

if time_casa not in times_disponiveis or time_fora not in times_disponiveis:
    print("\n[ERRO] Um ou ambos os times não foram encontrados. Certifique-se de digitar exatamente como listado acima.")
else:
    print(f"\n[OK] Analise: {time_casa} vs {time_fora}...")

    def calcular_expectativa_gols(df, casa, fora):
        # Médias gerais da Liga
        media_gols_casa_liga = (df['GolsCasa'].sum() / df.shape[0]).round(2)
        media_gols_fora_liga = (df['GolsVisitante'].sum() / df.shape[0]).round(2)
        
        stats_casa = df.loc[df['HomeTeam'] == casa]
        media_marcados_casa = stats_casa['GolsCasa'].mean()
        media_sofridos_casa = stats_casa['GolsVisitante'].mean()
        
        stats_fora = df.loc[df['AwayTeam'] == fora]
        media_marcados_fora = stats_fora['GolsVisitante'].mean()
        media_sofridos_fora = stats_fora['GolsCasa'].mean()
        
        forca_atq_casa = media_marcados_casa / media_gols_casa_liga
        forca_def_casa = media_sofridos_casa / media_gols_fora_liga
        
        forca_atq_fora = media_marcados_fora / media_gols_fora_liga
        forca_def_fora = media_sofridos_fora / media_gols_casa_liga
        
        xg_casa = (forca_atq_casa * forca_def_fora * media_gols_casa_liga).round(2)
        xg_fora = (forca_atq_fora * forca_def_casa * media_gols_fora_liga).round(2)
        
        return xg_casa, xg_fora

    def calcular_prob_gols(distribuicao, n_gols):
        contagem = np.sum(distribuicao[:100000] == n_gols)
        return contagem / 100000

    exp_casa, exp_fora = calcular_expectativa_gols(dados, time_casa, time_fora)
    print(f"Expectativa de gols: {time_casa} {exp_casa} x {exp_fora} {time_fora}" + '.')

    sim_casa = random.poisson(lam=exp_casa, size=100000)
    sim_fora = random.poisson(lam=exp_fora, size=100000)

    probs_casa = [calcular_prob_gols(sim_casa, i) for i in range(6)]
    probs_fora = [calcular_prob_gols(sim_fora, i) for i in range(6)]

    df_probs_casa = pd.DataFrame(probs_casa, columns=['Probs'])
    df_probs_fora = pd.DataFrame(probs_fora, columns=['Probs'])

    matriz = df_probs_casa.dot(df_probs_fora.T).round(3)
    print(' ')
    print('Matriz utilizada para calculo das probabilidades: ')
    print(matriz)

    prob_empate = np.trace(matriz.values)
    matriz_superior = matriz.where(np.triu(np.ones(matriz.shape)).astype(bool))
    
    vitoria_casa = matriz.sum().sum() - matriz_superior.sum().sum()
    vitoria_fora = matriz_superior.sum().sum() - prob_empate

    print("-" * 50)
    print(f"RESULTADOS CALCULADOS: ")
    print(f"Vitória {time_casa}: {round(vitoria_casa * 100, 1)}% (Odd: {round(1/vitoria_casa, 2)})")
    print(f"Empate: {round(prob_empate * 100, 1)}% (Odd: {round(1/prob_empate, 2)})")
    print(f"Vitória {time_fora}: {round(vitoria_fora * 100, 1)}% (Odd: {round(1/vitoria_fora, 2)})")
    
    print("-" * 50)
    print("Compare essas Odds com as da sua casa de apostas.")
    print("Se a Odd da casa for maior que a calculada aqui, pode haver valor.")
import time
import json
import os
from playwright.sync_api import sync_playwright

# --- Configuração ---
# Defina quantas rodadas você quer buscar. Para o campeonato completo, use 38.
RODADAS_A_BUSCAR = 38 
ARQUIVO_SAIDA = "dados_brasileirao.json"

def main():
    """
    Função principal que orquestra todo o processo de scraping.
    """
    print("Iniciando o processo de scraping do Brasileirão...")
    
    # Lista para armazenar os dados de todos os jogadores de todos os jogos
    dados_finais_jogadores = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Mude para False se quiser ver o navegador em ação
        page = browser.new_page()

        # --- FASE 1: Obter todos os IDs de eventos (jogos) ---
        print("\n--- Fase 1: Coletando IDs de todos os jogos ---")
        event_ids = []
        for i in range(1, RODADAS_A_BUSCAR + 1):
            url_rodada = f"https://www.sofascore.com/api/v1/unique-tournament/325/season/58766/events/round/{i}"
            try:
                page.goto(url_rodada, timeout=30000)
                json_text = page.locator('pre').inner_text()
                data_rodada = json.loads(json_text)
                
                events_da_rodada = data_rodada.get('events', [])
                for event in events_da_rodada:
                    if event.get('id'):
                        event_ids.append(event.get('id'))
                
                print(f"Rodada {i} de {RODADAS_A_BUSCAR}: {len(events_da_rodada)} jogos encontrados.")
                time.sleep(1) # Pausa para não sobrecarregar o servidor
            except Exception as e:
                print(f"Não foi possível buscar a rodada {i}. Erro: {e}")

        # Garante que não haja IDs duplicados
        event_ids = list(set(event_ids))
        print(f"\nTotal de {len(event_ids)} jogos únicos encontrados para analisar.")

        # --- FASE 2: Iterar sobre cada jogo para obter os dados detalhados ---
        print("\n--- Fase 2: Extraindo dados de chute a gol de cada jogo ---")
        for idx, event_id in enumerate(event_ids):
            print(f"Processando jogo {idx + 1} de {len(event_ids)} (ID: {event_id})...")
            
            try:
                # 1. Obter informações do evento (nomes dos times)
                url_evento = f"https://www.sofascore.com/api/v1/event/{event_id}"
                page.goto(url_evento, timeout=30000)
                json_evento_text = page.locator('pre').inner_text()
                data_evento = json.loads(json_evento_text).get('event', {})
                
                time_casa = data_evento.get('homeTeam', {}).get('name', 'Time da Casa Desconhecido')
                time_fora = data_evento.get('awayTeam', {}).get('name', 'Time de Fora Desconhecido')

                # 2. Obter o shotmap
                url_shotmap = f"https://www.sofascore.com/api/v1/event/{event_id}/shotmap"
                page.goto(url_shotmap, timeout=30000)
                json_shotmap_text = page.locator('pre').inner_text()
                data_shotmap = json.loads(json_shotmap_text)

                # 3. Processar e combinar os dados
                shots = data_shotmap.get('shotmap', [])
                if not shots:
                    print(f"  -> Jogo {event_id} não possui dados de shotmap. Pulando.")
                    time.sleep(1)
                    continue

                for shot in shots:
                    # Estrutura final do dicionário para cada chute
                    shot_info = {
                        'nome': shot.get('player', {}).get('name'),
                        'chute': shot.get('shotType'),
                        'coord_X': shot.get('playerCoordinates', {}).get('x'),
                        'coord_Y': shot.get('playerCoordinates', {}).get('y'),
                        'xg': shot.get('xg', 0),
                        'time': time_casa if shot.get('isHome') else time_fora
                    }
                    dados_finais_jogadores.append(shot_info)
                
                print(f"  -> Sucesso! {len(shots)} chutes adicionados para o jogo {time_casa} vs {time_fora}.")
                time.sleep(1) # Pausa entre cada jogo

            except Exception as e:
                print(f"  -> Erro ao processar o jogo {event_id}. Erro: {e}")

        browser.close()

    # --- FASE 3: Salvar todos os dados coletados em um único arquivo JSON ---
    print("\n--- Fase 3: Salvando todos os dados em um arquivo ---")
    try:
        with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
            json.dump(dados_finais_jogadores, f, ensure_ascii=False, indent=4)
        print(f"\nScraping concluído com sucesso! ✅")
        print(f"Todos os dados foram salvos no arquivo: {ARQUIVO_SAIDA}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")


if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import json,http.client
from urllib.parse import urlparse

OUTPUT_FILE = "dados_scraping.json"
event_ids = """[12116983,12116974,12116977,12116980,12116981,12116982,12116979,12116978,12116975,12116976, 12116976, 12116986, 12116984, 12116990,12116985, 12116991, 12116993, 12116989, 12116987, 12116988, 12376683, 12116997, 12116994, 12117000, 12116995, 12117001, 12116999, 12116996,12117002, 12116998, 12479063, 12117008, 12117012, 12117006, 12117007, 12117009, 12117011, 12117013, 12117004, 12117010, 12117017, 12117020,12117019, 12117021,12117016, 12117018,12117022, 12376871,12629260, 12117027, 12117032,12117031,12117026, 12117028,12376912, 12629257, 12357242,12369730, 12357205,12357233, 12357219,12357241, 12357197,12357227, 12357218,12357263,12359685, 12357122,12357103, 12357177,12357104, 12357143, 12357186, 12357162, 12356168, 12117060, 12117057, 12117061, 12117059, 12117056, 12117063, 12117062, 12117054, 12117058,12117055, 12117072, 12117068, 12117071, 12117073, 12117070, 12117065,12117064, 12117066, 12117067,12117069,12117083,12117082,12117081,12117076, 12117077, 12117075, 12117079, 12117080, 12117088, 12117085, 12117092, 12117089, 12117093, 12117086, 12117091, 12117084, 12117087,12117090, 12117102, 12117098, 12117095, 12117101, 12117094, 12117100, 12117103, 12117097, 12117096, 12117099, 12117112, 12117113, 12117108, 12117111, 12117105, 12117110, 12117106, 12117104, 12117109, 12117107, 12117117, 12117120, 12117115, 12117121, 12117123, 12117114, 12117122,12117119, 12117116, 12117118,12117124, 12117131, 12117128,12117133,12117125, 12117126, 12731927,12117136, 12117135, 12117143, 12117139,12117142, 12117140, 12117138, 12117141, 12117147, 12117148, 12117149, 12117144, 12117145, 12117146, 12117151, 12117153, 12117150, 12117152,12117154, 12117155, 12117160, 12117156, 12117162, 12117157, 12117159, 12727203, 12785268, 12117173, 12117169, 12117166, 12117168, 12117171, 12117170, 12117167, 12117165, 12117172, 12117164, 12117176, 12117178, 12117182, 12117183, 12117180, 12117181, 12117179, 12117177, 12117174, 12117175, 12117191, 12117192, 12117189, 12117185, 12117188, 12117193, 12117186, 12117187, 12117190, 12117184, 12117195, 12117194, 12117200, 12117197, 12117202, 12117203, 12117199, 12117201, 12117198, 12117196, 12117212, 12117209, 12117205, 12117206, 12117213, 12117211, 12117210, 12117204, 12117207, 12117208, 12117222, 12117218, 12117215, 12117214, 12117219, 12117221, 12117217, 12117223, 12117220, 12117216, 12117232, 12117231, 12117228, 12117233, 12117229, 12117230, 12117226, 12117225, 12117227, 12117224 ]"""
jogadores_info =[]

def obter_dados(event_id):
    
    #scrapping dados de shotmap
    url = f"https://www.sofascore.com/api/v1/event/{event_id}/shotmap"
    parsed_url = urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET",parsed_url.path)
    res = conn.getresponse()
    data = res.read()
    jsondata=json.loads(data.decode("utf-8"))

    #scrapping dados de casa/fora
    url2 = f"https://www.sofascore.com/api/v1/event/{event_id}"
    parsed_url2 = urlparse(url2)
    conn2 = http.client.HTTPSConnection(parsed_url2.netloc)
    conn2.request("GET",parsed_url2.path)
    res2 = conn2.getresponse()
    data2 = res2.read()
    jsondata2 = json.loads(data2.decode("utf-8"))


    #DF CASA/FORA
    casa = jsondata2['event']['homeTeam']['name']
    fora = jsondata2['event']['awayTeam']['name']

    #DF SHOTMAP
    if 'shotmap' in jsondata and jsondata['shotmap']:
        dados = jsondata['shotmap']

        for jogador in dados:
            nome = jogador['player']['name']
            chute = jogador['shotType']
            coord_X = jogador['playerCoordinates']['x']
            coord_Y = jogador['playerCoordinates']['y']
            xg = jogador.get('xg',0)
            isHome = jogador['isHome']
            time = casa if isHome else fora

            jogadores_info.append({
                'nome': nome,
                'chute':chute,
                'coord_X': coord_X,
                'coord_Y': coord_Y,
                'xg': xg,
                'time': time
            })
    else:
        print(f"Sem dados de shotmap para o evento {event_id}")

def obter_ids(rodada):
    i = 1
    while i <= rodada:
        url_id = f"https://www.sofascore.com/api/v1/unique-tournament/325/season/58766/events/round/{i}"
        print(url_id)
        parsed_url_id = urlparse(url_id)
        conn_id = http.client.HTTPSConnection(parsed_url_id.netloc)
        conn_id.request("GET",parsed_url_id.path)
        res_id = conn_id.getresponse()
        data_id = res_id.read()
        jsondata_id=json.loads(data_id.decode("utf-8"))
        
        ids = jsondata_id['events']

        for tags in ids:
            tag = tags['id']

            event_ids.append(tag)
        i +=1
    print(event_ids)

def salvar_dados_em_arquivo(dados, file_name):
    with open(file_name, 'w') as f:
        json.dump(dados, f, indent=4)

def carregar_dados_json(file_name):
    with open(file_name, 'r') as f:
        dados = json.load(f)
    return dados

_="""for event_id in event_ids:
    obter_dados(event_id)"""

_="""salvar_dados_em_arquivo(jogadores_info,OUTPUT_FILE)"""

jogadores_info = carregar_dados_json(OUTPUT_FILE)

df = pd.DataFrame(jogadores_info)

st.title("Brasileirão Série A 2024")
st.subheader("Filtre por qualquer time/jogador e veja todos os chutes!")
time = st.selectbox('Selecione um time',df['time'].sort_values().unique(),index=None)
jogador = st.selectbox('Selecione um jogador',df[df['time'] == time]['nome'].sort_values().unique(),index=None)

def filter_data(df,time,jogador):
    if time:
        df =df[df['time']==time]
    if jogador:
        df =df[df['nome']==jogador]
    
    return df

filtered_df = filter_data(df,time,jogador)

pitch = VerticalPitch(pitch_type='opta', half=True)
fig, ax = pitch.draw(figsize=(10,10))

def plot_shots(df,ax,pitch):
    for x in df.to_dict(orient = 'records'):
        pitch.scatter(
            x=100 - float(x['coord_X']),
            y=100 - float(x['coord_Y']),
            ax=ax,
            s=1000 * x['xg'],
            color='green' if x['chute'] == 'goal' else 'white',
            edgecolors='black',
            alpha=1 if x['chute'] == 'goal' else 0.5,
            zorder=2 if x['chute'] == 'goal' else 1
        )

plot_shots(filtered_df,ax,pitch)

st.pyplot(fig)
st.write("Pedro Bullé")

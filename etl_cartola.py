import requests
import pandas as pd


class BaseCartola():


    def __init__(self, url : str):
        self.url = url


    def pega_dataframes(self):
        """
          Função que faz o request na url da API do Cartola e retorna as bases de atletas e clubes

          Atributos:
              url: url na qual será feita a requisição pela lib requests (string)

          :return: df_atletas (df), df_clubes (df)
        """
        resposta = requests.get(self.url)
        df_atletas = pd.DataFrame(resposta.json()['atletas'])
        df_clubes = pd.DataFrame(resposta.json()['clubes'])
        return df_clubes, df_atletas


    def trata_dataframe_clubes(self):
        """
            Função que recebe o dataframe de clubes, trata e retorna o dataframe tratado.

            Atributos:
                df_clubes: dataframe de clubes (pd.Dataframe)

            :return: df_clubes_tratado (pd.Dataframe)
        """
        df_clubes = self.pega_dataframes()[0]
        df_clubes_tratado = df_clubes.T
        df_clubes_tratado = df_clubes_tratado[['abreviacao', 'escudos']]
        df_clubes_tratado.rename(
            columns={
                'abreviacao' : 'TIME',
                'escudos' : 'ESCUDO'},
            inplace = True)
        df_clubes_tratado.reset_index(drop=True, inplace=True)

        lista_escudos = []

        for i in range(len(df_clubes_tratado)):
          time = df_clubes_tratado['TIME'][i]
          escudo = df_clubes_tratado[df_clubes_tratado['TIME']==time]['ESCUDO'][i]['60x60']
          lista_escudos.append(escudo)

        df_clubes_tratado['ESCUDO'] = lista_escudos

        return df_clubes_tratado


    def adiciona_scouts_dicionario_individual(
        self,
        df_atletas: pd.DataFrame,
        local_dicionario: list,
        lista_scouts: list,
        prefixo_scouts: str):
        """
            Função que recebe o dataframe de atletas e uma lista de scouts,
            adiciona colunas dos scouts que estão dentro de algum dicionário e retorna.

            Atributos:
                - df_atletas: dataframe de atletas (pd.DataFrame)
                - local_dicionario: local no dataframe de atletas onde está o dicionário (list)
                - lista_scouts: lista com os nomes dos scouts (list)
                - prefixo_scouts: prefixo a ser adicionado no início do nome de cada scout (str)

            :return: df_atletas_dicionario
        """
        for scout in lista_scouts:
            coluna_scout = []
            for i in range(len(df_atletas)):
                try:
                    if len(local_dicionario) == 1:
                        nome_dicionario_1 = local_dicionario[0]
                        valor_scout = df_atletas[nome_dicionario_1][i][scout]
                    elif len(local_dicionario) == 3:
                        nome_dicionario_1 = local_dicionario[0]
                        nome_dicionario_2 = local_dicionario[1]
                        nome_dicionario_3 = local_dicionario[2]
                        valor_scout = df_atletas[nome_dicionario_1][i][nome_dicionario_2][nome_dicionario_3][scout]
                    else:
                        return 'local_dicionario incorreto'
                except:
                    valor_scout = 0
                coluna_scout.append(valor_scout)
            nome_coluna_scout = prefixo_scouts + scout
            df_atletas[nome_coluna_scout] = coluna_scout
        df_atletas_dicionario = df_atletas.copy()

        return df_atletas_dicionario


    def adiciona_scouts_varios_dicionarios(self):
        """
            Função que recebe o dataframe de atletas, adiciona colunas dos scouts que
            estão dentro de todos os dicionários e retorna.

            :return: df_atletas_dicionarios
        """
        lista_scouts = ['G', 'DP', 'A', 'SG', 'FT', 'FD', 'DS', 'DE', 'PS', 'FF', 'FS', 'I', 'FC', 'CA', 'GS', 'PC', 'CV', 'GC', 'PP']
        lista_gato_mestre = ['media_pontos_mandante', 'media_pontos_visitante', 'media_minutos_jogados', 'minutos_jogados']

        df_atletas = self.pega_dataframes()[1]

        df_atletas_dicionario_1 = self.adiciona_scouts_dicionario_individual(
            df_atletas = df_atletas,
            local_dicionario = ['scout'],
            lista_scouts = lista_scouts,
            prefixo_scouts = ''
            )

        df_atletas_dicionario_2 = self.adiciona_scouts_dicionario_individual(
            df_atletas = df_atletas_dicionario_1,
            local_dicionario = ['gato_mestre'],
            lista_scouts = lista_gato_mestre,
            prefixo_scouts = ''
            )

        df_atletas_dicionario_3 = self.adiciona_scouts_dicionario_individual(
            df_atletas = df_atletas_dicionario_2,
            local_dicionario = ['gato_mestre', 'scouts', 'media'],
            lista_scouts = lista_scouts,
            prefixo_scouts = 'media_'
            )

        df_atletas_dicionario_4 = self.adiciona_scouts_dicionario_individual(
            df_atletas = df_atletas_dicionario_3,
            local_dicionario = ['gato_mestre', 'scouts', 'mandante'],
            lista_scouts = lista_scouts,
            prefixo_scouts = 'mandante_'
            )

        df_atletas_dicionario_5 = self.adiciona_scouts_dicionario_individual(
            df_atletas = df_atletas_dicionario_4,
            local_dicionario = ['gato_mestre', 'scouts', 'visitante'],
            lista_scouts = lista_scouts,
            prefixo_scouts = 'visitante_'
            )

        df_atletas_dicionarios = df_atletas_dicionario_5.copy()

        return df_atletas_dicionarios


    def cria_media_basica(self):
        """
            Função que recebe o dataframe de atletas, adiciona colunas de média básica,
            incluindo total, mandante e visitante e retorna.

            Atributos:
                - df_atletas_dicionarios: dataframe de atletas (pd.DataFrame)

            :return: df_atletas_media_basica (pd.DataFrame)
        """
        df_atletas_dicionarios = self.adiciona_scouts_varios_dicionarios()
        df_atletas_media_basica = df_atletas_dicionarios.copy()
        df_atletas_media_basica['media_basica'] = df_atletas_media_basica['media_num'] - ( df_atletas_media_basica['G'] * 8 + df_atletas_media_basica['A'] * 5 + df_atletas_media_basica['SG'] * 5 ) / df_atletas_media_basica['jogos_num']
        df_atletas_media_basica['mandante_media_basica'] = df_atletas_media_basica['media_pontos_mandante'] - ( df_atletas_media_basica['mandante_G'] * 8 + df_atletas_media_basica['mandante_A'] * 5 + df_atletas_media_basica['mandante_SG'] * 5 ) / (df_atletas_media_basica['jogos_num'] / 2)
        df_atletas_media_basica['visitante_media_basica'] = df_atletas_media_basica['media_pontos_visitante'] - ( df_atletas_media_basica['visitante_G'] * 8 + df_atletas_media_basica['visitante_A'] * 5 + df_atletas_media_basica['visitante_SG'] * 5 ) / (df_atletas_media_basica['jogos_num'] / 2)

        return df_atletas_media_basica


    def trata_dataframe_atletas(self):
        """
            Função que recebe o dataframe de atletas, trata e retorna o dataframe tratado.

            Atributos:
                df_atletas: dataframe de atletas (pd.Dataframe)

            :return: df_atletas_tratado (pd.Dataframe)
        """
        df_atletas_media_basica = self.cria_media_basica()
        colunas_para_excluir = ['scout', 'atleta_id', 'gato_mestre', 'slug', 'apelido_abreviado', 'nome']
        df_atletas_filtrado = df_atletas_media_basica.drop(columns = colunas_para_excluir)
        """
        df_atletas_filtrado = df_atletas_media_basica[[
            'clube_id',
            'foto',
            'posicao_id',
            'apelido',
            'jogos_num',
            'status_id',
            'preco_num',
            'variacao_num',
            'pontos_num',
            'media_num',
            'minimo_para_valorizar'
        ]]
        """

        df_atletas_tratado = df_atletas_filtrado.copy()

        df_atletas_tratado .rename(
            columns = {
                'clube_id' : 'TIME',
                'foto' : 'FOTO',
                'posicao_id' : 'POSIÇÃO',
                'apelido' : 'JOGADOR',
                'jogos_num' : 'JOGOS',
                'status_id' : 'STATUS',
                'preco_num' : 'PREÇO',
                'variacao_num' : 'VAR(C$)',
                'pontos_num' : 'ULT',
                'media_num' : 'MÉDIA',
                'minimo_para_valorizar' : 'MIN P/ VAL'},
            inplace = True)

        df_atletas_tratado ['STATUS'] = df_atletas_tratado ['STATUS'].map(
            {2 : 'Dúvida',
            3 : 'Suspenso',
            5 : 'Contundido',
            6 : 'Nulo',
            7 : 'Provável'},
            na_action=None)

        df_atletas_tratado ['POSIÇÃO'] = df_atletas_tratado ['POSIÇÃO'].map(
            {1 : 'GOL',
            2 : 'LAT',
            3 : 'ZAG',
            4 : 'MEI',
            5 : 'ATA',
            6 : 'TEC'},
            na_action=None)

        df_atletas_tratado ['TIME'] = df_atletas_tratado ['TIME'].map(
            {262 : 'FLA',
            263 : 'BOT',
            264 : 'COR',
            265 : 'BAH',
            266 : 'FLU',
            267 : 'VAS',
            275 : 'PAL',
            276 : 'SAO',
            277 : 'SAN',
            280 : 'BGT',
            282 : 'CAM',
            283 : 'CRU',
            284 : 'GRE',
            285 : 'INT',
            290 : 'GOI',
            293 : 'CAP',
            294 : 'CFC',
            327 : 'AME',
            356 : 'FOR',
            1371 : 'CUI'},
            na_action=None)

        df_atletas_tratado.replace({'FORMATO': '220x220'}, regex=True, inplace=True)

        return df_atletas_tratado


    def cruza_dataframes(self):
        """
            Função que cruza os dataframes tratados de clubes e atletas, cruza as bases e retorna o resultado.

            Atributos:
                df_atletas_tratado: dataframe de atletas tratado (pd.DataFrame)
                df_clubes_tratado: dataframe de clubes tratado (pd.DataFrame)

            :return: df_cartola (pd.DataFrame)
        """
        df_clubes_tratado = self.trata_dataframe_clubes()
        df_atletas_tratado = self.trata_dataframe_atletas()

        df_cartola = pd.merge(df_atletas_tratado, df_clubes_tratado, how='left', on="TIME")

        return df_cartola
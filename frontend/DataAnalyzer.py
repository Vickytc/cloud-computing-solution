"""
Script Name: DataAnalyzer.py
Description: DataAnalyzer to do some data analysis and visualization
Authors:
    Luxi Bai(1527822)
    Wenxin Zhu (1136510)
    Ze Pang (955698) 
"""

import os
import json
import folium

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from shapely.geometry import shape, Point


def load_shp_file(shp_path):
    shp_df = gpd.read_file(shp_path)[["SA4_CODE21", "geometry"]]
    shp_df = shp_df.dropna(subset=['geometry'])
    shp_df['SA4_CODE21'] = shp_df['SA4_CODE21'].astype('string')
    shp_df['geometry'] = shp_df['geometry'].to_crs("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    return shp_df


def load_stopwords(stopwords_path):
    with open(stopwords_path, 'r', encoding='utf-8') as file:
        stopwords = set([line.strip() for line in file])
    return stopwords


class DataAnalyzer:
    def __init__(self, server, keyword=None):
        self.server = server
        self.keyword = keyword
        if keyword:
            self.json_filename = f"es_data/search_{server}_{keyword}.json"
            self.wordcloud_filename = f"es_data/wordcloud_{server}_{keyword}.json"
        else:
            self.json_filename = f"es_data/retrieve_{server}.json"
        self.df = None
        self.gdf = None


    def load_to_df(self):
        with open(self.json_filename, 'r', encoding='utf-8') as file:
            self.df = pd.DataFrame(json.load(file))
            if "created_at" in self.df:
                self.df['created_at'] = pd.to_datetime(self.df['created_at']).dt.date
            if "coordinates" in self.df:
                self.df['geometry'] = self.df['coordinates'].apply(lambda x: Point(x[0], x[1]))
                self.df = self.df.drop(columns=['coordinates'])


    def get_col_dist(self, on_col):
        negative_dist = self.df[(self.df[on_col] >= -1) & (self.df[on_col] < 0)][on_col]
        neutral_dist = self.df[self.df[on_col] == 0][on_col]
        positive_dist = self.df[(self.df[on_col] > 0) & (self.df[on_col] <= 1)][on_col]
        return {
            "Negative": negative_dist,
            "Neutral": neutral_dist,
            "Positive": positive_dist,
            }


    def get_col_count(self, on_col, ):
        negative_count = self.df[(self.df[on_col] >= -1) & (self.df[on_col] < 0)].shape[0]
        neutral_count = self.df[self.df[on_col] == 0].shape[0]
        positive_count = self.df[(self.df[on_col] > 0) & (self.df[on_col] <= 1)].shape[0]
        return {
            "Negative":negative_count,
            "Neutral":neutral_count,
            "Positive":positive_count,
            }


    def pie_plot(self, on_col, explode=None, colors=None):
        count_dict = self.get_col_count(on_col)
        plt.figure(figsize=(8, 8), facecolor="white")
        plt.pie(count_dict.values(), labels=count_dict.keys(), explode = explode, startangle=140, autopct='%1.1f%%', colors=colors)
        plt.title(f"{on_col.capitalize()} Distribution about {self.keyword} in {self.server.capitalize()}", fontsize=16)
        plt.tight_layout()
        plt.savefig(f"plots/pie_{self.server}_{self.keyword}.png")
        plt.show()


    def groupby(self, df, on_col, by_col, agg_func, reset_index):
        df_agg = df.groupby(by_col)[on_col].agg(agg_func)
        if reset_index:
            df_agg = df_agg.reset_index()
        return df_agg


    def groupby_plot(self, on_col, by_col, agg_func, reset_index=False):
        # Count the frequency of sentiment values for each date
        df_agg = self.groupby(self.df, on_col, by_col, agg_func, reset_index)

        # Plot the line chart
        plt.figure(figsize=(10, 6))
        df_agg.plot(kind='line')
        plt.title(f"Frequency of {self.server.capitalize()} related {self.keyword} topics over Time",  fontsize=16)
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"plots/freq_{self.server}_{self.keyword}.png")
        plt.show()

    
    def wordcloud_plot(self, stopwords):
        with open(self.wordcloud_filename, 'r', encoding='utf-8') as file:
            freq_dict = json.load(file)
        freq_dict = {word: freq for word, freq in freq_dict.items() if word not in stopwords}
        # Create the WordCloud object with the filtered frequencies
        wordcloud = WordCloud(background_color="white", width=800, height=400).generate_from_frequencies(freq_dict)
        # Plotting the WordCloud
        plt.figure(figsize=(12, 8))  # Setting the figure size
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(f"plots/wc_{self.server}_{self.keyword}.png")
        plt.show()


    def astype(self, on_col, to_type):
        self.df[on_col] = self.df[on_col].astype(to_type)


    def geo_plot(self, shp_df, on_col, by_col=None, agg_func=None,
                 reset_index=False, show_plot=False, save_plot=True):
        if "geometry" in self.df:
            gdf = gpd.GeoDataFrame(self.df, geometry='geometry')
            geo_data = gpd.sjoin(gdf, shp_df, how='inner', op='within')
        elif "sa4_code_2021" in self.df:
            geo_data = gpd.GeoDataFrame(pd.merge(self.df, shp_df, left_on="sa4_code_2021", right_on="SA4_CODE21"))
        
        if by_col:
            geo_data = self.groupby(geo_data, on_col, by_col, agg_func, reset_index)
        else:
            geo_data = geo_data

        geo_data = geo_data[['SA4_CODE21', on_col]].drop_duplicates('SA4_CODE21')
        # display(geoData)

        geo_json = shp_df[['SA4_CODE21','geometry']].drop_duplicates('SA4_CODE21').to_json()
        legend_map = {
            "sentiment": f"{agg_func} sentiment score",
            "med_tot_psnl_incom_weekly": "median total personal income weekly"
            }
        m = folium.Map(location=[-25.27, 133.77],  zoom_start=4)
        folium.Choropleth(
            geo_data=geo_json,
            data = geo_data,
            name="choropleth",
            columns = ["SA4_CODE21", on_col],
            key_on="feature.properties.SA4_CODE21",
            fill_color="RdPu",
            fill_opacity=1,
            line_opacity=1,
            legend_name=legend_map[on_col],
            nan_fill_color='white'
        ).add_to(m)
        if save_plot:
            filepath = f"plots/{self.server}_{self.keyword}_{on_col}.html" if self.keyword else f"plots/{self.server}_{on_col}.html"
            m.save(filepath)
        if show_plot:
            return m

import pandas as pd
import pylab as plt
import os
import yattag

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

cdf = pd.read_csv(r'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
hospital_df = pd.read_csv(r'https://opendata.arcgis.com/datasets/1044bb19da8d4dbfb6a96eb1b4ebf629_0.csv')

population_path = os.path.abspath(r'population.xlsx')
pdf = pd.read_excel(population_path)

pdf_fixed = pdf[pdf['COUNTY'] != 0]

mdf = pd.merge(cdf, pdf_fixed, 
            left_on=['state', 'county'],
            right_on=['STNAME', 'CTYNAME'],
            how='inner')

mdf['per_100k'] = mdf['cases'] / mdf['POPESTIMATE2019'] * 100000

print (mdf)
mean_len = 14

doc = yattag.Doc()
with doc.tag("body"):    
    with doc.tag('ul'):
        states = sorted(mdf['state'].unique())
        for state in states:
            with doc.tag('li'):
                doc.line('a', f'{state}', href = f'plots\\{state}\\index.html')                    
            state_doc = yattag.Doc()
            state_doc.line('h1', f'{state} Counties')
            state_path = os.path.join('plots', state)
            with state_doc.tag('table'):        
                
                if not os.path.exists(state_path):
                    os.mkdir(state_path)
                state_df = mdf[mdf['state'] == state]
                counties = state_df['county'].unique()
                
                for county in sorted(counties):
                    with state_doc.tag("tr"):
                        with state_doc.tag("td"):
                            ymin = 0
                            ymax = 15
                            county_df = state_df[state_df['county'] == county]
                            # county_df['per_100k_ra'] = county_df['per_100k'].rolling(7).mean()
                            county_df['new_cases'] = county_df['per_100k'].diff()
                            if len(county_df) > mean_len:
                                county_df['new_cases_ra'] = county_df['new_cases'].rolling(mean_len).mean()
                            county_path = os.path.join(state_path, county)

                            print (county_path)

                            plt.figure(figsize=(10, 10))

                            ax = plt.gca()

                            county_df.plot(x='date', y='new_cases', ax=ax, color = 'blue')
                            if len(county_df) > mean_len:
                                county_df.plot(x='date', y='new_cases_ra', ax=ax, color = 'black')
                            plt.title(f'{state} - {county}')

                            plt.xlabel('')

                            plt.xticks(rotation =45, fontsize='small')
                            xmin, xmax = plt.xlim()  
                            ymin_T, ymax_T = plt.ylim()
                            ymax = max(ymax, ymax_T)
                            
                            plt.axhspan(7, ymax, color = "purple", alpha = 0.5)
                            plt.axhspan(4, 7, color = "red", alpha = 0.5)
                            plt.axhspan(1, 4, color = "orange", alpha = 0.5)
                            plt.axhspan(ymin, 1, color = "yellow", alpha = 0.5)

                            #plt.axhline(y = county_df['new_cases'].iloc[-1], linestyle='dashed', color = 'blue')
                            if len(county_df) > mean_len:
                                plt.axhline(y = county_df['new_cases_ra'].iloc[-1], linestyle='dashed', color = 'black')                            
                                plt.axhline(y = county_df['new_cases_ra'].iloc[-7], linestyle='dotted', color = 'black')

                            yticks = list(plt.yticks()[0])
                            if len(county_df) > mean_len:
                                yticks.append(county_df['new_cases_ra'].iloc[-1])
                                yticks.append(county_df['new_cases_ra'].iloc[-7])

                            yticks = sorted(yticks)
                            plt.yticks(yticks)

                            plt.ylabel('Cases per 100k')
                            plt.subplots_adjust(bottom=0.15)
                            plt.grid()
                            plt.ylim(ymin, ymax)
                            
                            
                            plt.savefig(f'{county_path}.png')      
                            state_doc.line('a', county, id=f'#{county}')
                            state_doc.stag('img', src=f'{county}.png')  
                            # plt.show()
                            plt.clf()
                            county_df.to_csv(f'{county_path}.csv')
            with open(os.path.join(state_path, 'index.html'), 'w') as f:
                f.write(state_doc.getvalue())
with open('index.html', 'w') as f:
    f.write(doc.getvalue())      
    



    
    

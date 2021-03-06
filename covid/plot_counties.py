import pandas as pd
import pylab as plt
import os
import yattag
import csv

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

mdf['cases_per_100k'] = mdf['cases'] / mdf['POPESTIMATE2019'] * 100000
mdf['deaths_per_100k'] = mdf['deaths'] / mdf['POPESTIMATE2019'] * 100000
mdf['death_rate'] = mdf['deaths'] / mdf['cases']

print (mdf)
mean_len = 7

ff = open('infected.csv', 'w', newline='')
writer = csv.writer(ff)
doc = yattag.Doc()
with doc.tag("body"):    
    with doc.tag('ul'):
        states = sorted(mdf['state'].unique())
        for state in states:
        #for state in ['California']:
            with doc.tag('li'):
                doc.line('a', f'{state}', href = f'plots\\{state}\\index.html')                    
            state_doc = yattag.Doc()
            state_doc.line('h1', f'{state} Counties')
            state_path = os.path.join('plots', state)
            with state_doc.tag('table'):        
                
                if not os.path.exists(state_path):
                    os.mkdir(state_path)
                state_df = mdf[mdf['state'] == state].copy(deep=True)
                counties = state_df['county'].unique()
                
                for county in sorted(counties):
                    with state_doc.tag("tr"):
                        with state_doc.tag("td"):
                            
                            county_df = state_df[state_df['county'] == county].copy(deep=True)
                            # county_df['per_100k_ra'] = county_df['per_100k'].rolling(7).mean()
                            county_df['new_cases'] = county_df['cases'].diff()
                            county_df['new_cases_per_100k'] = county_df['cases_per_100k'].diff()
                            county_df['new_deaths'] = county_df['deaths_per_100k'].diff()
                            if len(county_df) > mean_len:
                                county_df['new_cases_per_100k_ra'] = county_df['new_cases_per_100k'].rolling(mean_len).mean()
                                county_df['new_deaths_ra'] = county_df['new_deaths'].rolling(mean_len).mean()
                                county_df['active_cases'] = county_df['new_cases'].rolling(8).sum()
                                county_df['infected_to_one'] = 1.0 / (county_df['active_cases'].multiply(4) / county_df['POPESTIMATE2019'])
                                rr = county_df.iloc[-1]
                                writer.writerow([rr['state'], rr['county'], rr['infected_to_one']])
                            county_path = os.path.join(state_path, county)

                            print (county_path)

                            plt.figure(figsize=(30, 25))
                            ymin = 0
                            ymax = 15
                            ax = plt.subplot(3, 2, 1)

                            county_df.plot(x='date', y='new_cases_per_100k', ax=ax, color = 'blue')
                            if len(county_df) > mean_len:
                                county_df.plot(x='date', y='new_cases_per_100k_ra', ax=ax, color = 'black')
                            plt.title(f'{state} - {county} - Cases per 100k')

                            plt.xlabel('')

                            plt.xticks(rotation =45, fontsize='small')
                            xmin, xmax = plt.xlim()  
                            ymin_T, ymax_T = plt.ylim()
                            ymax = max(ymax, ymax_T)
                            
                            plt.axhspan(7, ymax, color = "purple", alpha = 0.5)
                            plt.axhspan(4, 7, color = "red", alpha = 0.5)
                            plt.axhspan(1, 4, color = "orange", alpha = 0.5)
                            plt.axhspan(ymin, 1, color = "yellow", alpha = 0.5)

                            #plt.axhline(y = county_df['new_cases_per_100k'].iloc[-1], linestyle='dashed', color = 'blue')
                            if len(county_df) > mean_len:
                                plt.axhline(y = county_df['new_cases_per_100k_ra'].iloc[-1], linestyle='dashed', color = 'black')                            
                                plt.axhline(y = county_df['new_cases_per_100k_ra'].iloc[-7], linestyle='dotted', color = 'black')

                            yticks = list(plt.yticks()[0])
                            if len(county_df) > mean_len:
                                yticks.append(county_df['new_cases_per_100k_ra'].iloc[-1])
                                yticks.append(county_df['new_cases_per_100k_ra'].iloc[-7])

                            yticks = sorted(yticks)
                            plt.yticks(yticks)

                            plt.ylabel('Cases per 100k')
                            plt.grid()
                            plt.ylim(ymin, ymax)

                            ymin = 0
                            ymax = 0
                            ax = plt.subplot(3, 2, 2)
                            county_df.plot(x='date', y='new_deaths', ax=ax, color = 'blue')
                            if len(county_df) > mean_len:
                                county_df.plot(x='date', y='new_deaths_ra', ax=ax, color = 'black')
                            plt.title(f'{state} - {county} - Deaths per 100k')

                            plt.xlabel('')

                            plt.xticks(rotation =45, fontsize='small')
                            xmin, xmax = plt.xlim()  
                            ymin_T, ymax_T = plt.ylim()
                            ymax = max(ymax, ymax_T)
                            
                            if len(county_df) > mean_len:
                                plt.axhline(y = county_df['new_deaths_ra'].iloc[-1], linestyle='dashed', color = 'black')                            
                                plt.axhline(y = county_df['new_deaths_ra'].iloc[-7], linestyle='dotted', color = 'black')

                            yticks = list(plt.yticks()[0])
                            if len(county_df) > mean_len:
                                yticks.append(county_df['new_deaths_ra'].iloc[-1])
                                yticks.append(county_df['new_deaths_ra'].iloc[-7])

                            yticks = sorted(yticks)
                            plt.yticks(yticks)

                            plt.ylabel('Deaths per 100k')
                            plt.grid()
                            plt.ylim(ymin, ymax)



                            ymin = 0
                            ymax = 0
                            ax = plt.subplot(3, 2, 3)
                            county_df.plot(x='cases', y='deaths', ax=ax, color = 'blue')
                            plt.title(f'{state} - {county} - Deaths vs Cases')                            
                            plt.xticks(rotation =45, fontsize='small')
                            xmin, xmax = plt.xlim()  
                            ymin_T, ymax_T = plt.ylim()
                            ymax = max(ymax, ymax_T)

                            plt.ylabel('Deaths')
                            plt.xlabel('Cases')
                            plt.grid()
                            plt.ylim(ymin, ymax)



                            ymin = 0
                            ymax = 0
                            ax = plt.subplot(3, 2, 4)
                            county_df.plot(x='date', y='death_rate', ax=ax, color = 'blue')
                            plt.title(f'{state} - {county} - Death Rate')                            
                            plt.xticks(rotation =45, fontsize='small')
                            xmin, xmax = plt.xlim()  
                            ymin_T, ymax_T = plt.ylim()
                            ymax = max(ymax, ymax_T)

                            plt.ylabel('Deaths')
                            plt.xlabel('')
                            
                            plt.grid()
                            plt.ylim(ymin, ymax)


                            ymin = 0
                            ymax = 0
                            ax1 = plt.subplot(3, 2, 5)
                            county_df.plot(x='date', y='new_cases_per_100k_ra', ax=ax1, color = 'blue')                            
                            plt.title(f'{state} - {county} - Case to Death Phase Lag')                            
                            plt.xticks(rotation =45, fontsize='small')

                            ax2 = ax1.twinx()
                            county_df.plot(x='date', y='new_deaths_ra', ax=ax2, color = 'red')

                                                                          
                            # xmin, xmax = plt.xlim()  
                            # ymin_T, ymax_T = plt.ylim()
                            # ymax = max(ymax, ymax_T)

                            plt.ylabel('Deaths')
                            plt.xlabel('')
                            
                            plt.grid()
                            # plt.ylim(ymin, ymax)

                            ymin = 0
                            ymax = 0
                            ax1 = plt.subplot(3, 2, 6)
                            county_df.loc[county_df['date'] > '2020-05-01'].plot(x='date', y='infected_to_one', ax=ax1, color = 'red')                            
                            plt.title(f'{state} - {county} - 1 in X Cases')                            
                            plt.xticks(rotation =45, fontsize='small')
                            if len(county_df) > 8:
                                plt.axhline(y = county_df['infected_to_one'].iloc[-1], linestyle='dashed', color = 'black')                                       
                                yticks = list(plt.yticks()[0])
                                yticks.append(county_df['infected_to_one'].iloc[-1])
                                yticks = sorted(yticks)
                                plt.yticks(yticks)

                            plt.ylabel('Cases')
                            plt.xlabel('')                            
                            plt.grid()


                            plt.subplots_adjust(bottom=0.15)





                            
                            try:
                                plt.savefig(f'{county_path}.png')      
                            except:
                                print (f'Problem writing: {county_path} plot')
                            state_doc.line('a', county, id=f'#{county}')
                            state_doc.stag('img', src=f'{county}.png')  
                            # plt.show()
                            plt.clf()
                            plt.close()
                            county_df.to_csv(f'{county_path}.csv')
            with open(os.path.join(state_path, 'index.html'), 'w') as f:
                f.write(state_doc.getvalue())
with open('index.html', 'w') as f:
    f.write(doc.getvalue())      

ff.close()    



    
    

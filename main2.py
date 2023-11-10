import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from dotenv import load_dotenv

from database_utils import Database
from openai_utils import OpenAIAgent
from notification_utils import send_notification
from models import SupportTicket, Engineer

tickets_csv = """id,description,customer_country
1,"Hola, hemos notado que nuestro servicio VoLTE ha estado fallando desde ayer. ¿Podrían ayudarnos a solucionarlo pronto?",Spain
2,"Hi, our fiber optics networks seem to be damaged post the recent thunderstorm. The entire block is facing slow internet. Can you look into it? Regards, Nathan Hopkins\nOperation Manager\nWebsite: www.t-mobile.com\Quote of the Day: - Innovating Tomorrow, Today!",USA
3,"Hei, det har vært noen uventede nettverksavbrudd i vår region nylig. Kan du sjekke?",Norway
4,"Bonjour, nous rencontrons des problèmes de facturation. Il semble que nous soyons facturés deux fois pour le même service. Aidez-nous s'il vous plaît.",Canada
5,"Hey! I've been getting loads of unsolicited promotional calls lately. Is there a way to block them?",USA
6,"Hola, hemos intentado actualizar nuestro software de telecomunicaciones, pero enfrentamos algunos problemas de compatibilidad. ¿Puede asistir?",Spain
7,"Hey, it seems like our network is facing some congestion during peak hours. The internet speeds are extremely slow.",USA
8,"Hei, vi har problemer med å sette opp nye celle tårn i nordlige regioner. Trenger ekspertise.",Norway
9,"Bonjour, nous avons remarqué une chute de signal fréquente dans notre région. Pouvez-vous envoyer une équipe pour vérifier?",Canada
10,"The connection keeps dropping, and I have to restart the router multiple times a day. It's becoming a real inconvenience.",USA
"""

engineers_csv="""id,name,skillsets,workload,status,region,seniority,manager_email
1,Diego Martinez,"-Network Optimization -RF Engineering #VoIP Technologies",2,Working,Spain,5,diego.manager@empresa.com
2,Mike Johnson,"#Cybersecurity, Infrstructure anagement, -Telecom Software Proficiency",4,Working,USA,7,mike.manager@telecomus.com
3,Lars Olsen,"#Data Analytics -RF Engineering VoIP Technologies",3,Working,Norway,4,lars.manager@nortelecom.no
4,Charlotte Lefèvre,"Fiber Optics Expertise, #Billing Systems Knowledge, VoIP Technologies",2,Working,Canada,6,charlotte.manager@canadatele.com
5,Elena Suarez,"#Project Management -Telecom Software Proficiency, RF Engineering",3,Working,Spain,5,elena.manager@empresa.com
6,Brian Wilson,"Infrastructure Management, Cybersecurity",2,"On Vacation",USA,6,brian.manager@telecomus.com
7,Emil Johansen,"-Network Optimization -Data Analytics",1,Working,Norway,5,emil.manager@nortelecom.no
8,Juliette Dubois,"#Billing Systems Knowledge, -Telecom Software Proficiency",3,Working,Canada,6,juliette.manager@canadatele.com
9,Carlos Ortega,"-RF Engineering #Infrastructure Management, Cybersecurity",2,Working,Spain,7,carlos.manager@empresa.com
10,Grace Adams,"Telecom Software Proficiency | VoIP Technologies",3,Working,USA,6,grace.manager@telecomus.com
"""

def visualize_matching_scores_small(df):
    # Extract necessary columns
    engineers = df['name'].tolist()
    scores = df['matching_score'].tolist()
    
    # Setting colors based on matching score
    colors = ['green' if score > 80 else 'yellow' if score > 50 else 'red' for score in scores]
    
    plt.figure(figsize=(10, 6))
    plt.barh(engineers, scores, color=colors)
    plt.xlabel('Matching Score')
    plt.ylabel('Engineer Name')
    plt.title('Engineer Matching Scores for the Ticket')
    for i, v in enumerate(scores):
        plt.text(v, i, " "+str(round(v, 2)), va='center', color='black', fontweight='bold')
    plt.tight_layout()
    
    # Display on Streamlit
    st.pyplot(plt)


def visualize_matching_scores(df):
    engineers = df['name'].tolist()
    scores = df['matching_score'].tolist()
    regions = df['region'].tolist()
    statuses = df['status'].tolist()
    workloads = df['workload'].tolist()

    # Setting colors based on matching score
    #colors = ['green' if score > 80 else 'yellow' if score > 50 else 'red' for score in scores]
    colors = ['green' if status == 'Working' else 'red' for status in statuses]

    plt.figure(figsize=(12, 8))

    for i, (score, engineer, color, region, status, workload) in enumerate(zip(scores, engineers, colors, regions, statuses, workloads)):
        # Bar for in-region engineers
        #if region == "in-region":
        plt.barh(engineer, score, color=color, hatch='' if workload <= 3 else '///')
        # Circle for out-of-region engineers
        #else:
            #plt.scatter(score, i, s=150, color=color, edgecolors='black', hatch='' if status == "Working" else '///', label=engineer)

        # Display score
        plt.text(score, i, " "+str(round(score, 2)), va='center', color='black', fontweight='bold')

    plt.xlabel('Matching Score')
    plt.ylabel('Engineer Name')
    plt.title('Engineer Matching Scores for the Ticket')
    plt.tight_layout()

    # Display on Streamlit
    st.pyplot(plt)

def main():

    db = Database(engineers_csv, tickets_csv)
    # Set your OpenAI API key here
    if os.getenv('HOSTNAME') == 'E-5CG24202NG':
      load_dotenv('../.env')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    agent = OpenAIAgent(openai_api_key)
    
    st.title("Engineer Matcher for Support Tickets")
    
    # Load tickets from the database
    # Assuming a get_all_tickets function that fetches all tickets
    tickets_df = db.get_all_tickets()

    # Display tickets in a dropdown menu
    col1, col2,col3 = st.columns([1,2,4])
    with col1:
      selected_ticket_id = st.selectbox("Select a ticket:", tickets_df['id'].values)
    if selected_ticket_id:
      with col2:
        selected_country = tickets_df['customer_country'][tickets_df['id'] == selected_ticket_id].iloc[0]
        st.markdown(f"**Customer Country**")
        st.write(selected_country)
      with col3:
        selected_description = tickets_df['description'][tickets_df['id'] == selected_ticket_id].iloc[0]
        st.markdown(f"**Description for Ticket {selected_ticket_id}:**")
        st.write(selected_description)
    
    if st.button('Find Matching Engineers'):
        # Fetch selected ticket
        ticket = db.get_ticket_by_id(int(selected_ticket_id))

        # Get all available engineers
        engineers = db.get_engineers(int(selected_ticket_id))
        print(f"......engineers: {engineers}")
        print(f"......type(engineers): {type(engineers)}")

        print(f"ticket_id: {selected_ticket_id},,, ticket: {ticket}")
        # Find the best matching engineers
        df = agent.get_matching_engineers(ticket, engineers)
        print(f"df.columns: {df.columns}")


        newdf=pd.DataFrame(list(df['engineer']))
        print(f"newdf: {newdf}")
        newdf = pd.concat([newdf, df['matching_score']], axis=1)

        # Filter the top 3 matching engineers and exclude those with 0% match
        df = newdf.head(3)

        if len(df) == 0:
            st.warning("No matching engineers found for the selected ticket.")
        else:
            #st.dataframe(df[['engineer_name', 'engineer_skillsets', 'matching_score']])
            st.markdown(f"**All engineers in {selected_country}:**")
            st.dataframe(df)
            st.success(f"Top {len(df)} matching engineers displayed!")
            visualize_matching_scores(df)

    query = st.text_input("Enter db query:")
    if st.button("Submit"):
        result=db.query_db(query)
        st.write(result)

if __name__ == '__main__':
    main()

from dotenv import load_dotenv
load_dotenv()

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search,scrape_url
import os

#model setup
llm =ChatOllama(
    model="gemma4:31b",
    base_url="https://ollama.com",
    temperature=0,
     client_kwargs={
        "headers": {
            "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
        }
    }
)

#1st Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

#2nd Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

#writer chain(runnables)
writer_prompt=ChatPromptTemplate.from_messages([
    ("system","You are an expert research writer. Write clear ,structured and insightful reports."),

    ("human","""Write a detailed research report on the topic below.
    Topic:{topic}
    Research GAthered:
    {research}
    
    Structure the report as:
    -Introduction
    -Key Findings (mimimum 3 well-explained points)
    -Conclusion
    -Sources(list all URLs found in the research)
    
    Be detailed, factual and professional."""),

])

writer_chain=writer_prompt | llm | StrOutputParser()


#critc_chain
critic_prompt=ChatPromptTemplate([
    ("system","You are a sharp and constructive research critic.Be honest and specific."),
    ("human","""Review the research report below and evaluate it strictly.
    
    Report:
    {report}
    
    Respond in this exact format:
   
     Score:X/10
     
     Strengths:
     -...
     -...
     
     Sreas to Improve:
     -...
     -...
     
     One line verdict:
     ..."""),
])


critic_chain=critic_prompt | llm | StrOutputParser()

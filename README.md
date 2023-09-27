<br>
<p align="center"><a href="https://audrey.kr/"><img width=60% src="https://github.com/san9min/OpenAI_SKT/assets/92682815/15fc53df-8a49-4c1d-a825-0ed026fefd31" alt="logo"></a></p>
<h4 align="center">
 <a href="https://github.com/audreyaiai/OpenAI_SKT">AI</a> &nbsp;&nbsp; | &nbsp;&nbsp; <a href="https://github.com/san9min/OpenAI_SKT">Frontend</a> &nbsp;&nbsp; | &nbsp;&nbsp; <a href="https://github.com/audreyaiai/OpenAI_SKT_BE">Backend</a>
</h4>
<br>




# audrey.ai

<h3 align="center"><br>✨&nbsp; TEAM&nbsp; ✨<br><br></h3>
<p align="center">
<b>🚀 <a href="https://github.com/san9min">Sangmin Lee</a></b> <br>
<b>🐋 <a href="https://github.com/SUNGBEOMCHOI">Sungbeom Choi</a></b> <br>
<b>🦄 <a href="https://github.com/devch1013">ChanHyuk Park</a></b> <br>
<b>🌟 <a href="https://github.com/0601p">Minsu Park</a></b> <br>
<br><br>
<hr>
 
**[Demo Page](https://audrey.kr/)**  

We are developing an AI-powered online research tool aimed at streamlining repetitive and time-consuming tasks in online data research. Our goal is to enable individuals to focus on more important tasks by harnessing the capabilities of generative AI technology.

We plan to start by collecting data from trusted sources such as **[통계청](https://kostat.go.kr)** and **[정책 브리핑](http://www.korea.kr)**, and then establish partnerships with other data-rich websites to expand our vector database. This will allow us to provide valuable and reliable information for research purposes.

Our tool will be versatile, capable of handling a wide range of data formats, including web pages, PDF documents, YouTube videos, and even audio content. This flexibility ensures that users can extract information from diverse sources efficiently.

To make our tool even more user-friendly and productive, we will implement an autonomous agent that can understand and execute user commands effectively. This agent will serve as a valuable assistant, helping users navigate and extract information from the vast pool of data available online.

In summary, our AI-powered online research tool aims to enhance the productivity and efficiency of data research by automating repetitive tasks, providing access to reliable data sources, and incorporating an autonomous agent to assist users in their research endeavors.




## Agent
<br>
<p align="center"><a href="https://audrey.kr/"><img width=60% src="https://github.com/san9min/OpenAI_SKT/assets/92682815/6b4c3dc5-8cb1-46aa-8f67-16251578e53d" alt="agent"></a></p>


To make GPT more useful, we introduce *Agent*. it has been enhanced to understand human language, think autonomously, and make judgments to use appropriate **tools**.

It can now retrieve necessary information from databases or the web, and, based on the found data or numerical information, it is equipped to draw graphs or charts as required.


## Chunking Strategy

<p align="center"><img width=100% src="https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/77cef516-43b6-45bc-a9a8-8b28a26657af" alt="chunking"></p>
We conducted extensive preprocessing to ensure that GPT could better understand the data. This involved removing noise information (such as Ads, navigation bars, etc) and incorporating visual data to comprehend context and structural details.


We obtained official authorization and fine-tuned Faster RCNN on a dataset comprising 200 images from the **통계청 (Korean Statistical Office)** and **정부 브리핑 (Government Briefings)**. 
Through this process, we are able to divide each chunk into the following categories by utilizing the visual information
<p align="center">

| Category            | Description                                                         |
|:---------------------:|:---------------------------------------------------------------------:|
| Topic               | Identifying the central subject or theme of the content.          |
| Title               | Recognizing and understanding the document or presentation's title. |
| Contents            | Grasping the textual information within the document or presentation. |
| Figure              | Identifying visual elements such as images or illustrations.       |
| Graph               | Recognizing and interpreting graphical representations of data.    |
| Table               | Understanding tabular data structures.                             |
| Table Caption       | Recognizing and comprehending captions associated with tables.     |
| Comment             | Identifying and understanding comments or annotations within the content. |
</p>
This comprehensive preprocessing and fine-tuning approach enhances GPT's ability to process and categorize information effectively, making it more proficient in analyzing textual and visual data in a structured manner.


## Embedding


![audrey AI_본선](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/06d6576f-35cc-4d63-915b-8c5e13858e38)

When you do research, you'll be collecting a variety of data types. We've made it possible to receive multiple types of data, not just text.

## Pipeline
![image](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/90ef67e3-bca9-4115-9a22-fa6fa78b7e57)


Design our pipeline to work with you through the entire process


## Backend Structure
<p align="center"><img width=80% src="https://github.com/san9min/OpenAI_SKT/assets/92682815/f17c88da-661b-4b9b-9d41-7dd346e139e6" alt="backend"></a></p>


## Result

### Semantic Search
![audrey AI_본선](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/a75ac6e8-12df-4a50-9d5f-48bf6b1c9af0)

통계청 only returns results when keywords are matched, which makes searching difficult. We provide valuable material that is semantically similar.


### Table Understanding

![audrey AI_본선](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/f70213a8-fcc9-49f4-8020-cb1c5e933947)

Tables contain a lot of useful information that has a structural counterpart. However, if you scrape them directly into text, GPT can't understand them very well and can't utilize them.
In order to understand tables well, it is important to preprocess the structure of the table into a form that GPT can understand, rather than just scraping it. When scraping the table as it was, GPT didn't utilize the table information. But with our chunking method, the table was better understood and utilized.

### Graph Tool (Agent)
![audrey AI_본선](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/98826687-2bd4-4df4-a590-19a0676665da)

GPT outputs text by default, so it can't generate visuals like graphs. 
We give our agents tools, so they can write Python code to plot graphs based on the information they receive as text.


### Report

![image](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/c9819a1e-a699-4042-8243-c8621eb527cd)

This is the first draft of our model. Based on the data we put in, model write a good draft with useful tables and thumbnail images (from DALL-E).

## Citations

```bibtex
@misc{embedchain,
  author = {Taranjeet Singh},
  title = {Embedchain: Framework to easily create LLM powered bots over any dataset},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/embedchain/embedchain}},
}
```

```bibtex
@article{shen2021layoutparser,
  title={LayoutParser: A Unified Toolkit for Deep Learning Based Document Image Analysis},
  author={Shen, Zejiang and Zhang, Ruochen and Dell, Melissa and Lee, Benjamin Charles Germain and Carlson, Jacob and Li, Weining},
  journal={arXiv preprint arXiv:2103.15348},
  year={2021}
}
```


<!-- FOOTER START -->
<p align="center"><a href="#">
    <img width="100%" height="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1167b1,100:03254c&height=180&section=footer&animation=fadeIn&fontAlignY=40" alt="header" />
</a></p>
<!-- FOOTER END -->

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


To make GPT more useful, it has been enhanced to understand human language, think autonomously, and make judgments to use appropriate tools.

It can now retrieve necessary information from databases or the web, and, based on the found data or numerical information, it is equipped to draw graphs or charts as required.


## Chunking Strategy
<p align="center"><img width=100% src="https://github.com/san9min/OpenAI_SKT/assets/92682815/d3805e72-64a9-4571-a64e-29ac4b73b897" alt="chunking"></p>
We conducted extensive preprocessing to ensure that GPT could better understand the data. This involved removing noise information and incorporating visual data to comprehend context and structural details.


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
![audrey AI_본선](https://github.com/audreyaiai/OpenAI_SKT/assets/92682815/e91c51d6-661d-4403-884d-acd42fab48b7)


## Backend Structure
<p align="center"><img width=80% src="https://github.com/san9min/OpenAI_SKT/assets/92682815/f17c88da-661b-4b9b-9d41-7dd346e139e6" alt="backend"></a></p>




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

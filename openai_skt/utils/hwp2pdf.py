# 1, libreoffice 설치 (아래는 우분투에서 설치 방법)
# sudo apt-get install libreoffice
# 2, unoconv 설치
# pip install unoconv
# 3, libreoffice 한글 extension 설치
# https://extensions.libreoffice.org/en/extensions/show/27504
# 위 확장의 깃은 https://github.com/ebandal/H2Orestart 여기 readme 참고하면 편할 듯
# 4, libreoffice 켜두기!

import subprocess

def hwp2pdf(infile, outfile, envname):
    # openai_skt 폴더를 기준으로 infile, outfile을 지정, envname으로는 unoconv가 설치된 env 이름을 넣으면 됨
    subprocess.run(f"conda run -n {envname} unoconv -f pdf -o {outfile} {infile}", shell=True)

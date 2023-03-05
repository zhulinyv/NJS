echo 正在进行换源操作……
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo 正在安装Poetry……
pip install poetry

echo 正在安装依赖，耗时较长，耐心等待……
poetry run pip install aiocache==0.11.1
poetry run pip install aiofiles==0.8.0
poetry run pip install aiohttp==3.8.3
poetry run pip install aiosignal==1.2.0
poetry run pip install aiosqlite==0.17.0
poetry run pip install amis-python==1.0.6
poetry run pip install anyio==3.6.2
poetry run pip install appdirs==1.4.4
poetry run pip install APScheduler==3.9.1.post1
poetry run pip install arrow==1.2.3
poetry run pip install asgiref==3.5.2
poetry run pip install async-timeout==4.0.2
poetry run pip install attrs==22.1.0
poetry run pip install bbcode==1.1.0
poetry run pip install beautifulsoup4==4.11.1
poetry run pip install bidict==0.22.0
poetry run pip install binaryornot==0.4.4
poetry run pip install bs4==0.0.1
poetry run pip install cachetools==5.2.0
poetry run pip install certifi==2022.9.24
poetry run pip install chardet==5.0.0
poetry run pip install charset-normalizer==2.1.1
poetry run pip install chevron==0.14.0
poetry run pip install click==8.1.3
poetry run pip install cn2an==0.5.17
poetry run pip install colorama==0.4.6
poetry run pip install contourpy==1.0.6
poetry run pip install cookiecutter==1.7.3
poetry run pip install cssselect==1.2.0
poetry run pip install cycler==0.11.0
poetry run pip install dateparser==1.1.1
poetry run pip install dnspython==2.2.1
poetry run pip install ecdsa==0.18.0
poetry run pip install EdgeGPT==0.0.51
poetry run pip install emoji==2.1.0
poetry run pip install et-xmlfile==1.1.0
poetry run pip install expandvars==0.9.0
poetry run pip install expiringdict==1.2.2
poetry run pip install Faker==16.4.0
poetry run pip install fastapi==0.88.0
poetry run pip install feedparser==6.0.10
poetry run pip install filelock==3.8.2
poetry run pip install fonttools==4.38.0
poetry run pip install frozenlist==1.3.1
poetry run pip install gitdb==4.0.9
poetry run pip install githubkit==0.9.6
poetry run pip install GitPython==3.1.29
poetry run pip install greenlet==1.1.3
poetry run pip install h11==0.12.0
poetry run pip install h2==4.1.0
poetry run pip install hpack==4.0.0
poetry run pip install httpcore==0.14.7
poetry run pip install httptools==0.5.0
poetry run pip install httpx==0.22.0
poetry run pip install huggingface-hub==0.11.1
poetry run pip install humanize==4.4.0
poetry run pip install hyperframe==6.0.1
poetry run pip install idna==3.4
poetry run pip install imageio==2.22.2
poetry run pip install importlib-metadata==4.12.0
poetry run pip install iso8601==1.1.0
poetry run pip install jieba==0.42.1
poetry run pip install Jinja2==3.1.2
poetry run pip install jinja2-time==0.2.0
poetry run pip install joblib==1.2.0
poetry run pip install kiwisolver==1.4.4
poetry run pip install littlepaimon-utils==1.0.2
poetry run pip install loguru==0.6.0
poetry run pip install lxml==4.9.1
poetry run pip install Markdown==3.4.1
poetry run pip install MarkupSafe==2.1.1
poetry run pip install matplotlib==3.6.2
poetry run pip install msgpack==1.0.4
poetry run pip install multidict==6.0.2
poetry run pip install nb-cli==0.6.7
poetry run pip install nonebot-adapter-onebot==2.2.0
poetry run pip install nonebot-adapter-qqguild==0.1.4
poetry run pip install nonebot-bison==0.5.5
poetry run pip install nonebot-plugin-apscheduler==0.2.0
poetry run pip install nonebot-plugin-chatrecorder==0.2.1
poetry run pip install nonebot-plugin-datastore==0.4.0
poetry run pip install nonebot-plugin-easy-translate==0.1.3
poetry run pip install nonebot-plugin-gocqhttp==0.6.7
poetry run pip install nonebot-plugin-guild-patch==0.2.2
poetry run pip install nonebot-plugin-htmlrender==0.2.0.1
poetry run pip install nonebot-plugin-imageutils==0.1.13.4
poetry run pip install nonebot-plugin-localstore==0.2.0
poetry run pip install nonebot2==2.0.0rc2
poetry run pip install numpy==1.23.4
poetry run pip install openai==0.27.0
poetry run pip install OpenAIAuth==0.0.3.1
poetry run pip install opencv-python-headless==4.6.0.66
poetry run pip install openpyxl==3.0.10
poetry run pip install packaging==21.3
poetry run pip install paho-mqtt==1.6.1
poetry run pip install pandas==1.5.2
poetry run pip install pandas-stubs==1.5.2.221124
poetry run pip install parsel==1.7.0
poetry run pip install peewee==3.15.3
poetry run pip install Pillow==9.3.0
poetry run pip install playwright==1.27.1
poetry run pip install poyo==0.5.0
poetry run pip install proces==0.1.2
poetry run pip install prompt-toolkit==3.0.32
poetry run pip install psutil==5.9.4
poetry run pip install py-cpuinfo==8.0.0
poetry run pip install pyasn1==0.4.8
poetry run pip install pydantic==1.10.2
poetry run pip install pyee==8.1.0
poetry run pip install pyfiglet==0.8.post1
poetry run pip install Pygments==2.13.0
poetry run pip install pygtrie==2.5.0
poetry run pip install PyJWT==2.6.0
poetry run pip install pymdown-extensions==9.5
poetry run pip install pymongo==4.3.2
poetry run pip install pyparsing==3.0.9
poetry run pip install pypika-tortoise==0.1.6
poetry run pip install pypinyin==0.47.1
poetry run pip install python-dateutil==2.8.2
poetry run pip install python-dotenv==0.21.0
poetry run pip install python-engineio==4.3.4
poetry run pip install python-jose==3.3.0
poetry run pip install python-markdown-math==0.8
poetry run pip install python-slugify==6.1.2
poetry run pip install python-socketio==5.7.2
poetry run pip install pytz==2022.6
poetry run pip install pytz-deprecation-shim==0.1.0.post0
poetry run pip install pywebio==1.6.2
poetry run pip install PyYAML==6.0
poetry run pip install qrcode==7.3.1
poetry run pip install regex==2022.3.2
poetry run pip install requests==2.28.1
poetry run pip install rfc3986==1.5.0
poetry run pip install rply==0.7.8
poetry run pip install rsa==4.9
poetry run pip install rtoml==0.9.0
poetry run pip install ruamel.yaml==0.17.21
poetry run pip install ruamel.yaml.clib==0.2.7
poetry run pip install scikit-learn==1.1.3
poetry run pip install scipy==1.9.3
poetry run pip install setuptools-scm==7.0.5
poetry run pip install sgmllib3k==1.0.0
poetry run pip install Shapely==1.8.5.post1
poetry run pip install six==1.16.0
poetry run pip install smmap==5.0.0
poetry run pip install sniffio==1.3.0
poetry run pip install soupsieve==2.3.2.post1
poetry run pip install SQLAlchemy==1.4.41
poetry run pip install sqlalchemy2-stubs==0.0.2a29
poetry run pip install sqlmodel==0.0.8
poetry run pip install starlette==0.22.0
poetry run pip install tencentcloud-sdk-python==3.0.754
poetry run pip install text-unidecode==1.3
poetry run pip install threadpoolctl==3.1.0
poetry run pip install tinydb==4.7.0
poetry run pip install tls-client==0.1.5
poetry run pip install tokenizers==0.13.2
poetry run pip install tomli==2.0.1
poetry run pip install tomlkit==0.10.2
poetry run pip install tornado==6.2
poetry run pip install tortoise-orm==0.19.2
poetry run pip install tqdm==4.64.1
poetry run pip install transformers==4.25.1
poetry run pip install types-pytz==2022.6.0.1
poetry run pip install typing_extensions==4.4.0
poetry run pip install tzdata==2022.6
poetry run pip install tzlocal==4.2
poetry run pip install ua-parser==0.15.0
poetry run pip install ujson==5.5.0
poetry run pip install urllib3==1.26.12
poetry run pip install user-agents==2.2.0
poetry run pip install uvicorn==0.20.0
poetry run pip install w3lib==2.1.1
poetry run pip install watchfiles==0.18.1
poetry run pip install watchgod==0.8.2
poetry run pip install wcwidth==0.2.5
poetry run pip install websockets==10.4
poetry run pip install win32-setctime==1.1.0
poetry run pip install wordcloud==1.8.2.2
poetry run pip install yarl==1.8.1
poetry run pip install zhconv==1.4.3
poetry run pip install zipp==3.8.1

echo 安装完成，按任意键退出
pause
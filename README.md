# Learning-Records

项目结构说明
```
Learning-Records/
├── README.md                   项目说明文件
├── MindMap/                    思维导图
|   └── Subjects/               思维导图主题
|       └── mind_map_files      具体的思维导图文件
└── References/                 可方便引用的论文学习记录
    ├── Template.md             论文学习记录 markdown 模板
    ├── server.py               调用 LLM 自动根据 uri 与指定模板生成学习记录的 MCP Server
    ├── client.py               用于调用 server.py 的 MCP Client
    └── Subjects/               论文主题
        ├── markdown_files      具体的论文学习记录文件
        └── Resources/          资源文件夹
            └── resource_files  供 markdown 学习记录插入的图片等资源
```

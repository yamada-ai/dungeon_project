# dungeon_project

## 実行
```
$ pip install -r requirements.txt
$ python server.py
```

## 仕様

### モード
1. 部屋間の移動の学習
2. 部屋内での移動の学習
3. 本番

### API
#### /init 
POST  
request
```json
{
  "seed": int,
  "mode": int,
  "reward": list[int], // まだ未定
}
```
response
```json
{
  "id": int,
}
```

#### /info/id
GET  
response
```json
{
  "roomId": int,
}
```
```json
{
  "roomId": int,
  "x": int,
  "y": int,
  "enemies": [
    {
      "x": int,
      "y": int,
    }
  ],
"map": {
  "cells": list[list[int]],
  "rooms": [
    {
      "id": int,
      "origin": 
    }
  ]
}
}
```

#### /action/id
POST  
request
```json
{
  "action": int, // 次の部屋のid
}
```
```json
{
  "action": {
    "action": int,
    "nextRoomId": int,
  }
}
```
response
```json
{
  "reward": float,
  "roomId": int,
}
```
```json
{
  "reward": float,
  "roomId": int,
  "x": int,
  "y": int,
  "enemies": [
    {
      "x": int,
      "y": int,
    }
  ],
  "map": {
    
  }
}
```

#### /reset/id
POST  
request
```json
{}
```
response
```json
{}
```


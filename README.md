# dungeon_project

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
  "room_id": int,
}
```
```json
{
  "room_id": int,
  "x": int,
  "y": int,
  "enemy": [
    {
      "x": int,
      "y": int,
    }
  ]
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
  "action": int, // 行動 
}
```
response
```json
{
  "reward": float,
  "room_id": int,
}
```
```json
{
  "reward": float,
  "room_id": int,
  "x": int,
  "y": int,
  "enemy": [
    {
      "x": int,
      "y": int,
    }
  ]
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


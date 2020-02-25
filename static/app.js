var app = new Vue({
    el: '#app',
    data: {
        mode: "2",
        seed: -1,
        raw: '',
        id: 'NO DATA',
        isEnd: false,
        map: [],
        floor_map: [[]],
        reward: 0,
    },
    created(){
        document.onkeydown = () => {
            this.on_keydown(event.keyCode)
        }
    },
    methods: {
        createSimulator: async function () {
            let data = {
                mode: parseInt(this.mode)
            };
            if(this.seed !== -1){
                data['seed'] = parseInt(this.seed);
            }
            await axios
                .post('/init', data)
                .then(response => {
                    this.raw = response.data
                    this.id = response.data.id
                });
            this.refresh();
        },
        setData: function(data){
            this.raw = data;
            this.isEnd = data.isEnd;
            this.floor_map = data.map.cells;
            let room = data.map.rooms[data.roomId];
            if (this.isEnd) {
                if (this.floor_map[data.y + room.origin[0]][data.x + room.origin[1]] === 5) {
                    this.reset();
                    return
                }
                this.floor_map[data.y + room.origin[0]][data.x + room.origin[1]] = 6;
            } else {
                this.floor_map[data.y + room.origin[0]][data.x + room.origin[1]] = 3;
            }
            data.enemies.forEach(enemy => {
                if(enemy.x > -1 && enemy.y > -1){
                    this.floor_map[enemy.y + room.origin[0]][enemy.x + room.origin[1]] = 4;
                }
            });
        },
        reset: function(){
            (async () => {
                await axios.post('/reset/' + this.id);
                this.refresh();
            })();
        },
        refresh: function(){
            axios
            .get('/info/'+this.id)
            .then(response => {
                if(this.mode == "1"){
                    console.log(response.data);
                    this.raw = response.data;
                }else{
                    this.setData(response.data);
                }
            })
        },
        postAction: function(data){
            axios.post('/action/'+this.id, data).then(response => {
                this.setData(response.data);
            });
        },
        up: function(){
            this.postAction({ action: 1 });
        },
        down: function(){
            this.postAction({ action: 3 });
        },
        left: function(){
            this.postAction({ action: 4 });
        },
        right: function(){
            this.postAction({ action: 2 });
        },
        attack: function(){
            this.postAction({ action: 0 });
        },
        on_keydown(keyCode){
            console.log(keyCode);
            if(this.isEnd){
                return
            }
            switch(keyCode){
                case 65:
                    this.left();
                    break;
                case 87:
                    this.up();
                    break;
                case 68:
                    this.right();
                    break;
                case 83:
                    this.down();
                    break;
                case 74:
                    this.attack();
                    break;
            }
        }
    },
});

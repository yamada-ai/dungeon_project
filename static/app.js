var app = new Vue({
    el: '#app',
    data: {
        raw: '',
        id: 'NO DATA',
        isEnd: false,
        map: [],
        floor_map: [[]]
    },
    created(){
        document.onkeydown = () => {
            this.on_keydown(event.keyCode)
        }
    },
    methods: {
        createSimulator: function(){
            console.log('create');
            axios
            .get('/create')
            .then(response => {
                this.raw = response.data;
                this.id = response.data.id
            });
        },
        refresh: function(){
            console.log('refresh');
            axios
            .get('/info/'+this.id)
            .then(response => {
                this.raw = response.data;
                this.isEnd = response.data.isEnd;
                this.floor_map = response.data.map;
                if(this.isEnd) {
                    this.floor_map[response.data.agent.y][response.data.agent.x] = 6;
                }else{
                    this.floor_map[response.data.agent.y][response.data.agent.x] = 3;
                }
                response.data.enemies.forEach(element => {
                    this.floor_map[element.y][element.x] = 4;
                });
            })
        },
        on_keydown(keyCode){
            console.log(keyCode);
            if(this.isEnd){
                return
            }
            switch(keyCode){
                case 65:
                    axios.post('/action/'+this.id, {
                        action: 4
                    });
                    break;
                case 87:
                    axios.post('/action/' + this.id, {
                        action: 1
                    });
                    break;
                case 68:
                    axios.post('/action/' + this.id, {
                        action: 2
                    });
                    break;
                case 83:
                    axios.post('/action/' + this.id, {
                        action: 3
                    });
                    break;
                case 74:
                    axios.post('/action/' + this.id, {
                        action: 0
                    });
            }
            this.refresh()
        }
    },
});

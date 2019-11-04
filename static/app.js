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
        createSimulator: async function () {
            console.log('create');
            await axios
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
                    if(this.floor_map[response.data.agent.y][response.data.agent.x] === 5){
                        (async () => {
                            await this.createSimulator();
                            this.refresh();
                        })();
                        return
                    }
                    this.floor_map[response.data.agent.y][response.data.agent.x] = 6;
                }else{
                    this.floor_map[response.data.agent.y][response.data.agent.x] = 3;
                }
                response.data.enemies.forEach(element => {
                    this.floor_map[element.y][element.x] = 4;
                });
            })
        },
        up: function(){
            axios.post('/action/' + this.id, {
                action: 1
            });
            this.refresh();
        },
        down: function(){
            axios.post('/action/' + this.id, {
                action: 3
            });
            this.refresh();
        },
        left: function(){
            axios.post('/action/' + this.id, {
                action: 4
            });
            this.refresh();
        },
        right: function(){
            axios.post('/action/' + this.id, {
                action: 2
            });
            this.refresh();
        },
        attack: function(){
            axios.post('/action/' + this.id, {
                action: 0
            });
            this.refresh();
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

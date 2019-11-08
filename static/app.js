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
        setData: function(data){
            this.raw = data;
            this.isEnd = data.isEnd;
            this.floor_map = data.map;
            if (this.isEnd) {
                if (this.floor_map[data.agent.y][data.agent.x] === 5) {
                    (async () => {
                        await this.createSimulator();
                        this.refresh();
                    })();
                    return
                }
                this.floor_map[data.agent.y][data.agent.x] = 6;
            } else {
                this.floor_map[data.agent.y][data.agent.x] = 3;
            }
            data.enemies.forEach(element => {
                this.floor_map[element.y][element.x] = 4;
            });
        },
        refresh: function(){
            console.log('refresh');
            axios
            .get('/info/'+this.id)
            .then(response => {
                this.setData(response.data);
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

var app = new Vue({
    el: '#app',
    data: {
        raw: '',
        list: [],
        log: '',
        floor_map: [[]],
        index: 0,
    },
    async mounted() {
        await axios.get('/log/list').then(response => {
            this.list = response.data.list;
            if(this.list.length > 0){
                this.log = this.list[0];
            }
        });
    },
    created() {
        document.onkeydown = () => {
            this.onKeyDown(event.keyCode);
        };
    },
    methods: {
        getList: function(){
            axios.get('/log/list').then(response => {
                this.list = response.data.list;
            });
        },
        getLogData: function(){
            this.index = 0;
            axios.get('/log/'+this.log).then(response => {
                this.raw = response.data;
                this.setAgent();
            });
        },
        setAgent: function(){
            this.floor_map = JSON.parse(JSON.stringify(this.raw.cellMap));
            let agent = this.raw.moveLog[this.index].agent;
            let enemies = this.raw.moveLog[this.index].enemies;
            this.floor_map[agent.y][agent.x] = 3;
            enemies.forEach(e => {
                if(e.x !== -1 && e.y !== -1){
                    this.floor_map[e.y][e.x] = 4;
                }
            });
        },
        prev: function(){
            this.index -= 1;
            if(this.index <= 0){
                this.index = 0;
            }
            this.setAgent();
        },
        next: function(){
            this.index += 1;
            if(this.index > this.raw.moveLog.length-1){
                this.index = this.raw.moveLog.length-1;
            }
            this.setAgent();
        },
        onKeyDown: function(keyCode){
            switch(keyCode){
                case 37:
                    this.prev();
                    break;
                case 39:
                    this.next();
                    break;
            }
        },
    },
    watch: {
        log: function(){
            this.getLogData();
        }
    },
})
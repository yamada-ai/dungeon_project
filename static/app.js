var app = new Vue({
    el: '#app',
    data: {
        raw: '',
        id: 'NO DATA',
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
                this.raw = response.data
                this.id = response.data.id
            });
        },
        refresh: function(){
            console.log('refresh');
            axios
            .get('/info/'+this.id)
            .then(response => {
                this.raw = response.data
                this.map = response.data.map
                this.floor_map = this.map.floor_map
                this.floor_map[response.data.agent.y][response.data.agent.x] = 3
            })
        },
        on_keydown(keyCode){
            console.log(keyCode)
            switch(keyCode){
                case 65:
                    axios.post('/action/'+this.id, {
                        action: 4
                    })
                    break
                case 87:
                    axios.post('/action/' + this.id, {
                        action: 1
                    })
                    break
                case 68:
                    axios.post('/action/' + this.id, {
                        action: 2
                    })
                    break
                case 83:
                    axios.post('/action/' + this.id, {
                        action: 3
                    })
                    break
            }
            this.refresh()
        }
    },
})
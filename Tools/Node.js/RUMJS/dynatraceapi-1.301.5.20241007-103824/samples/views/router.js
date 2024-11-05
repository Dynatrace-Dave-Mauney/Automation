class Router {
    constructor() {
        this.routes = [];
    }

    get(group, callback) {
        if (!group || !callback) throw new Error('group or callback must be given');

        if (typeof group !== "string") throw new TypeError('typeof group must be a string');
        if (typeof callback !== "function") throw new TypeError('typeof callback must be a function');

        this.routes.forEach( function (route) {
            if(route.group === group) throw new Error(`the group ${route.group} already exists`);
        });

        const route = { group, callback };
        this.routes.push(route);
    }

    go(route) {
        window.location.hash = route;
        this.init();
    }

    init() {
        this.routes.some(function ({ group, callback }) {
            let hash = window.location.hash;
            hash = hash.split("#")[1];

            const fn = match(group, {
                decode: decodeURIComponent
            });

            if (fn(hash)) {
                let req = { name: hash, group };
                return callback.call(this, req);
            }
        })
    }
}

L.TileLayer.ChinaProvider = L.TileLayer.extend({

  initialize: function(type, options) { // (type, Object)
    var providers = L.TileLayer.ChinaProvider.providers;

    var parts = type.split('.');

    var providerName = parts[0];
    var mapName = parts[1];
    var mapType = parts[2];

    console.log("mmYY:"+ providerName+"   "+ mapName+"   "+mapType );
    var url = providers[providerName][mapName][mapType];
    console.log("mmYY:"+url);
    options.subdomains = providers[providerName].Subdomains;

    L.TileLayer.prototype.initialize.call(this, url, options);
    }
});


L.TileLayer.ChinaProvider.providers = {
    GaoDe: {
        Normal: {
//          Map: 'http://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
       		Map: 'img/{z}/{x}/{y}.png',
        },
        Satellite: {
//          Map: 'http://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
 			Map: 'img/{z}/{x}/{y}.png',
//          Annotion: 'http://webst0{s}.is.autonavi.com/appmaptile?style=8&x={x}&y={y}&z={z}'
       		Annotion: 'img/{z}/{x}/{y}.png'
        },
        Subdomains: ["0","1", "2", "3", "4"]
    },

};

L.tileLayer.chinaProvider = function(type, options) {
    return new L.TileLayer.ChinaProvider(type, options);
};

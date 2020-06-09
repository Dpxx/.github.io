// create the slippy map
var map = L.map('image-map', {
    minZoom: 0,
    maxZoom: 7,
    center: [0, 0],
    zoom: 0,
    crs: L.CRS.Simple,
    zoomControl: false
});

var imgs = new L.layerGroup();
function setPics(level,center_x,center_y){
  //imgs.clearLayers();
  //var x0 = imgs.getLayers();
  var n = 2**level;
  // dimensions of the image
  var w = 960;
  var wb = w/n;
  // url = 'img/'+level+'/'+y+'/'+x+'.png';
  // calculate the edges of the image, in coordinate space
  var southWest = map.unproject([0, w], 0);
  var northEast = map.unproject([w, 0],0);
  var bounds = new L.LatLngBounds(southWest, northEast);

  var x = Math.trunc(center_x/wb);
  var y = Math.trunc(-center_y/wb);
  console.log(x,y);
  for (var i = -1;i < 2;i++){
    for (var j = -1;j < 2;j++){
      if (x+i>=0 && x+i<n && y+j>=0 && y+j<n) {
        var southWest1 = map.unproject([(x+i)*wb, (y+j)*wb],0);
        var northEast1 = map.unproject([(x+1+i)*wb,(y+1+j)*wb], 0);
        var bounds1 = new L.LatLngBounds(southWest1, northEast1);
        L.imageOverlay('img/'+level+'/'+(x+i)+'/'+(y+j)+'.png', bounds1).addTo(imgs);
      }
    }
  }
  //The following lines is the first edition which load all pics.
  // for (var y = 0;y < n; y++) {
  //   for (var x = 0; x < n; x++) {
  //     var southWest1 = map.unproject([y*wb, x*wb],0);
  //     var northEast1 = map.unproject([(y+1)*wb,(x+1)*wb], 0);
  //     var bounds1 = new L.LatLngBounds(southWest1, northEast1);
  //     L.imageOverlay('img/'+level+'/'+y+'/'+x+'.png', bounds1).addTo(imgs);
  //   }
  // };
  imgs.addTo(map);
  map.setMaxBounds(bounds);
  // tell leaflet that the map is exactly as big as the image
  // add the image overlay,
  // so that it covers the entire map
  // var imgLayer0 = L.imageOverlay('img/'+1+'/'+0+'/'+0+'.png', bounds0);
  // var imgLayer1 = L.imageOverlay('img/'+1+'/'+0+'/'+1+'.png', bounds1);
  // var imgLayer2 = L.imageOverlay('img/'+1+'/'+1+'/'+0+'.png', bounds2);
  // var imgLayer3 = L.imageOverlay('img/'+1+'/'+1+'/'+1+'.png', bounds3);
  // var imgLayers = L.layerGroup([imgLayer0,imgLayer1,imgLayer2,imgLayer3]).addTo(map);
  // imgs.clearLayers();
  //for (var im = 0; im < x0.length; im++){
  //	imgs.removeLayer(x0[im]);
  //}
};
function delPics(level){
	
  //imgs.clearLayers();
  var x0 = imgs.getLayers();
  var n;
  switch(level) {
    case 0:
      n = 1;
      break;
    case 1:
      n = 4;
      break;
    default:
        n = 9;
  };
  for (var im = 0; im < n; im++){
		imgs.removeLayer(x0[im]);
	}
};

var ini_level = 0;
setPics(0,0,0);

map.on('zoomstart', function(e){
  ini_level = map.getZoom();
});
map.on('zoomend', function(e){
  level = map.getZoom();
  console.log("zoom changed." + level);
  document.getElementById('text1').textContent = "当前放大层数 : " + level;
  setPics(level,map.getCenter().lng,map.getCenter().lat);
  setTimeout( function(){delPics(ini_level);console.log("The picture of the previous layer has been deleted")}, 2 * 100 );//延迟200毫秒
});

map.on('click', function(e){
  console.log("center:"+map.getCenter());
  console.log("clicked position:"+e.latlng.lat+"/"+e.latlng.lng);
  L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
});
map.on('dragend', function(e){
  imgs.clearLayers();
  level = map.getZoom();
  setPics(level,map.getCenter().lng,map.getCenter().lat);
});

// L.DomEvent.on(document.getElementById('image-map'), 'mousewheel', function(e) {
//   console.log(e);
//   console.log(L.DomEvent.getMousePosition(e));
// });
L.control.zoom({
    zoomInTitle: '放大',
    zoomOutTitle: '缩小'
}).addTo(map);

// 使用 TileLayer 类来继承实现.
L.TileLayer.ChinaProvider = L.TileLayer.extend({

  initialize: function(type, options) { // (type, Object)
    var providers = L.TileLayer.ChinaProvider.providers;

    var parts = type.split('.');

    var providerName = parts[0];
    var mapName = parts[1];
    var mapType = parts[2];

    var url = providers[providerName][mapName][mapType];
    options.subdomains = providers[providerName].Subdomains;

    L.TileLayer.prototype.initialize.call(this, url, options);
    }
});


L.TileLayer.ChinaProvider.providers = {
    MyMap: {
        Normal: {
       		Map: 'img/{z}/{x}/{y}.png',
        },
        Satellite: {
 		Map: 'img/{z}/{x}/{y}.png',
       		Annotion: 'img/{z}/{x}/{y}.png'
        },
        Subdomains: ["0","1", "2", "3", "4"]
    },
};

L.tileLayer.chinaProvider = function(type, options) {
    return new L.TileLayer.ChinaProvider(type, options);
};

var normalm = L.tileLayer.chinaProvider('MyMap.Normal.Map', {
    maxZoom: 7,
    minZoom: 0,
    tileSize: 256
});

var normal = L.layerGroup([normalm]);

var map_1 = L.map("map", {
    center: [0, 0],
    zoom: 2,
    layers: [normal],
    zoomControl: false
});

L.control.zoom({
    zoomInTitle: '放大',
    zoomOutTitle: '缩小'
}).addTo(map_1);

map_1.on('zoomend', function(e){
  level = map_1.getZoom();
  console.log("zoom changed." + level);
  document.getElementById('text2').textContent = "当前放大层数 : " + level;
});

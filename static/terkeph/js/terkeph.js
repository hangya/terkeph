var map;

// set default view settings
var currentlat = 47.497914;
var currentlng = 19.040200;
var currentzoom = 8;
var currentmaptype = 'p';

function updateHash() {
    document.location.hash = '#'+currentlat.toString()+
        '+'+currentlng.toString()+
        '+'+currentzoom.toString()+
        '+'+currentmaptype;
}

function parserUrl() {
    return encodeURIComponent('https://terkeph.hangya.net/parse?lat='+currentlat.toString()+'&lng='+currentlng.toString()+'&zoom='+currentzoom.toString()+'&type='+currentmaptype)
}

var findUserSelect = document.createElement('select');
findUserSelect.id = 'finduserselect'
findUserSelect.style.width = '90px';

function ProhardverControl(container, map) {
//ProhardverControl.prototype = new google.maps.Control();
//ProhardverControl.prototype.initialize = function(map) {
    //var container = document.createElement('div');
    
    var addUserDiv = document.createElement('div');
    this.setButtonStyle_(addUserDiv);
    container.appendChild(addUserDiv);
    addUserDiv.appendChild(document.createTextNode('beállítás'));
    google.maps.event.addDomListener(addUserDiv, 'click', function() {
        if (!map.add_point) {
            map.add_point = new google.maps.Marker({
	        position: map.getCenter(),
	        map: map,
                draggable: true,
                dragCrossMove: true,
                raiseOnDrag: true
		//animation: google.maps.Animation.DROP
            });
            google.maps.event.addListener(map.add_point, 'dragstart', function() {
                map.add_iw.close();
            });
	    map.add_iw = new google.maps.InfoWindow({
	      position: map.add_point.getPosition(),
	      maxWidth: 300,
	      pixelOffset: new google.maps.Size(0, -25)
	    });
            map.add_point.updateInfoWindow = function () {
	        map.add_iw.setPosition(map.add_point.getPosition());
                
                addPointForm = document.createElement('form');
                addPointForm.action = 'https://prohardver.hu/muvelet/privat/uj.php?dstid='+robot_id+'&url='+parserUrl();
                addPointForm.method = 'post';
                
                addPointText = document.createTextNode('A TérkéPH!-re való felkerüléshez, vagy új elhelyezkedés megadásához fogd meg az alábbi pöcköt, húzd a megfelelő helyre, majd kattints ');
                addPointForm.appendChild(addPointText);
                
                addPointInput = document.createElement('input');
                addPointInput.name = 'content';
                addPointInput.type = 'hidden';
                addPointInput.defaultValue = ''
                addPointInput.value = 'app=map\naction=add\npoint='+map.add_point.getPosition().toUrlValue();
                addPointForm.appendChild(addPointInput);
                
                addPointSubmit = document.createElement('input');
                addPointSubmit.name = 'submit';
                addPointSubmit.type = 'submit';
                addPointSubmit.defaultValue = '';
                addPointSubmit.value = 'ide!';
                addPointForm.appendChild(addPointSubmit);
                
                map.add_iw.setContent(addPointForm);
		map.add_iw.open(map);
            };
            google.maps.event.addListener(map.add_point, 'dragend', function () {
                map.add_point.updateInfoWindow()
            });
            //map.addOverlay(map.add_point);
            map.add_point.updateInfoWindow()
        } else {
            map.add_point.setPosition(map.getCenter());
            map.add_point.updateInfoWindow()
        }
        
    });
    
    var delUserDiv = document.createElement('div');
    this.setButtonStyle_(delUserDiv);
    container.appendChild(delUserDiv);
    delUserDiv.appendChild(document.createTextNode('törlés'));
    google.maps.event.addDomListener(delUserDiv, 'click', function() {
        var answer = confirm('Biztosan le szeretnél kerülni a TérkéPH!-ről?\n\nTipp: Ha csak át szeretnéd helyezni magad, ahhoz elég beállítani egy új helyet.')
        if (answer) {
            
            var delUserForm = document.createElement('form');
            delUserForm.action = 'https://prohardver.hu/muvelet/privat/uj.php?dstid='+robot_id+'&url='+parserUrl();
            delUserForm.method = 'post';
            
            var delUserInput = document.createElement('input');
            delUserInput.name = 'content';
            delUserInput.type = 'hidden';
            delUserInput.defultValue = '';
            delUserInput.value = 'app=map\naction=del';
            delUserForm.appendChild(delUserInput);
            
            delUserDiv.appendChild(delUserForm);
            delUserForm.submit();
        }
    });
    
    var findUserDiv = document.createElement('div');
    this.setButtonStyle_(findUserDiv);
    container.appendChild(findUserDiv);
    findUserDiv.appendChild(findUserSelect);
    
    //map.getContainer().appendChild(container);
    //return container;
}

//ProhardverControl.prototype.getDefaultPosition = function() {
//    return new google.maps.ControlPosition(google.maps.ANCHOR_BOTTOM_RIGHT, new google.maps.Size(10, 20));
//}

ProhardverControl.prototype.setButtonStyle_ = function(button) {
    button.style.textDecoration = 'none';
    button.style.color = '#B42224';
    button.style.backgroundColor = '#CDC5AF';
    button.style.font = 'bold 13px Verdana,Arial,Helvetica,sans-serif';
    button.style.border = '1px solid #8C7D6C';
    button.style.padding = '2px';
    button.style.marginBottom = '3px';
    button.style.textAlign = 'center';
    button.style.width = '100px';
    button.style.cursor = 'pointer';
}
function initialize() {
  var MAP_TYPES = {
    'm': google.maps.MapTypeId.ROADMAP,
    'h': google.maps.MapTypeId.HYBRID,
    'k': google.maps.MapTypeId.SATELLITE,
    'p': google.maps.MapTypeId.TERRAIN
  };
  var TYPES_ARRAY = []
  for (map_type in MAP_TYPES) { 
    TYPES_ARRAY.push(MAP_TYPES[map_type]); 
  }

  map = new google.maps.Map(document.getElementById('map-canvas'), { 
    mapTypeControlOptions: {mapTypeIds: TYPES_ARRAY},
    mapTypeControl: true,
    animatedZoom: false
  });

  var prohardverControlDiv = document.createElement('div');
  var prohardverControl = new ProhardverControl(prohardverControlDiv, map);
  prohardverControlDiv.index = 1;
  map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(prohardverControlDiv);

//  map.addControl(new google.maps.LocalSearch());
//  map.addControl(new ProhardverControl())


  
  if (document.location.hash.length > 1) {
    frags = document.location.hash.substr(1).split('+');
    if (!isNaN(parseFloat(frags[0]))) { currentlat = parseFloat(frags[0]); }
    if (!isNaN(parseFloat(frags[1]))) { currentlng = parseFloat(frags[1]); }
    if (!isNaN(parseInt(frags[2]))) { currentzoom = parseFloat(frags[2]); }
    if (frags[3] in MAP_TYPES) { currentmaptype = frags[3]; }
  }
  updateHash();

  map.setCenter(new google.maps.LatLng(currentlat, currentlng));
  map.setZoom(currentzoom);
  map.setMapTypeId(MAP_TYPES[currentmaptype]);


  google.maps.event.addListener(map, 'dragend', function() {
    currentlat = map.getCenter().lat();
    currentlng = map.getCenter().lng();
    currentzoom = map.getZoom();
    updateHash();
  });
  google.maps.event.addListener(map, 'maptypeid_changed', function() {
    for (map_type in MAP_TYPES) {
      if (MAP_TYPES[map_type] == map.getMapTypeId()) {
        currentmaptype = map_type;
      }
    }
    updateHash();
  });


        
  // show points
  $.getJSON('/users', function(data) {
         
    // put points onto the map
    for (var i=0; i<data.length; i++) { // last one is empty
      var marker = createMarker(data[i]);
      //map.addOverlay(marker);
    }
            
    // generate user select
    var option = document.createElement('option')
    option.value='';
    option.appendChild(document.createTextNode((data.length).toString()+' pont...'));
    findUserSelect.appendChild(option);
            
    for (var i=0; i<data.length; i++) {
      var option = document.createElement('option')
      option.value = data[i][3]
      option.appendChild(document.createTextNode(data[i][1]));
      findUserSelect.appendChild(option);
    }
           
    findUserSelect.onchange = function() {
      c = findUserSelect.options[findUserSelect.selectedIndex].value;
      c = c.split(',');
      if (c.length == 2) {
        currentlat = parseFloat(c[0]);
        currentlng = parseFloat(c[1]);
        currentzoom = 15;
        map.setCenter(new google.maps.LatLng(currentlat, currentlng));
	map.setZoom(currentzoom);
        updateHash();
      }
    };        
  });
}


function createMarker(input) {
  var latlng = input[3].split(',', 2);
  var marker = new google.maps.Marker({
    position: new google.maps.LatLng(parseFloat(latlng[0]), parseFloat(latlng[1])),
    map: map,
    icon: {
      anchor: new google.maps.Point(25, 25),
      url: 'https://prohardver.hu/dl/faces/' + input[2] + '.gif'
    },
    title: input[1]
  });

  google.maps.event.addListener(marker, 'click', function() {
    window.open('https://prohardver.hu/tag/' + input[0]+ '.html', 
      input[0], 
      'top=80,left=190,width=656,height=650,titlebar,menubar,scrollbars,resizable');
  });
  return marker;
}

google.maps.event.addDomListener(window, 'load', initialize);




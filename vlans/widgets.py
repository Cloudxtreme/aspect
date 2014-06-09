### -*- coding: utf-8 -*- 
from django.conf import settings
from django import forms
from vlans.JSONField import JSONField
from django.core.serializers.json import DjangoJSONEncoder
import json
#from django.utils import simplejson as json
from django.utils.safestring import mark_safe  

DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 400

DEFAULT_LAT = 60.00
DEFAULT_LNG = 30.00
DEFAULT_ADDRESS = u'(Не задан)'

class LocationWidget(forms.TextInput):
    def __init__(self, *args, **kw):
        self.map_width = kw.get("map_width", DEFAULT_WIDTH )
        self.map_height = kw.get("map_height", DEFAULT_HEIGHT )

        super(LocationWidget, self).__init__(*args, **kw)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        if value is None:
            lat, lng, address = DEFAULT_LAT, DEFAULT_LNG, DEFAULT_ADDRESS
            value = {'lat': lat, 'lng': lng, 'address': address}
        else:
            d = json.loads(value) # Запаковываем строку в JSON object
            lat, lng, address = float(d['lat']), float(d['lng']), d['address']
            #lat, lng, address = float(value['lat']), float(value['lng']), value['address']
        curLocation = json.dumps(value, cls=DjangoJSONEncoder)
        elevation = 0
        js = '''
<script type="text/javascript">
//<![CDATA[
    var map_%(functionName)s;
    var elevator;
    var infowindow = new google.maps.InfoWindow();

    function savePosition_%(functionName)s(point, address, elevation)
    {
        var input = document.getElementById("id_%(name)s");
        var location = {'lat': point.lat().toFixed(6), 'lng': point.lng().toFixed(6)};
        location.address = '%(defAddress)s';
        if (address) {
            location.address = address;
        }
        input.value = JSON.stringify(location);
        map_%(functionName)s.panTo(point);
    }

    function load_%(functionName)s() {
        var point = new google.maps.LatLng(%(lat)f, %(lng)f);

        var options = {
            zoom: 13,
            center: point,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        map_%(functionName)s = new google.maps.Map(document.getElementById("map_%(name)s"), options);

        geocoder = new google.maps.Geocoder();

        elevator = new google.maps.ElevationService();

        var marker = new google.maps.Marker({
            map: map_%(functionName)s,
            position: point,
            draggable: true
        });
        
        google.maps.event.addListener(marker, 'dragend', function(mouseEvent) {
            geocoder.geocode({'latLng': mouseEvent.latLng}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK && results[0]) {
                    $('#address_%(name)s').val(results[0].formatted_address);
                    savePosition_%(functionName)s(mouseEvent.latLng, results[0].formatted_address);
                }
                else {
                    savePosition_%(functionName)s(mouseEvent.latLng);
                }
            });
        });

        google.maps.event.addListener(map_%(functionName)s, 'click', function(mouseEvent){
            marker.setPosition(mouseEvent.latLng);
            geocoder.geocode({'latLng': mouseEvent.latLng}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK && results[0]) {
                    $('#address_%(name)s').val(results[0].formatted_address);
                    savePosition_%(functionName)s(mouseEvent.latLng, results[0].formatted_address);
                }
                else {
                    savePosition_%(functionName)s(mouseEvent.latLng);
                }
            });
        });

        $('#address_%(name)s').autocomplete({
            source: function(request, response) {
                geocoder.geocode({'address': request.term}, function(results, status) {
                    response($.map(results, function(item) {
                        return {
                            value: item.formatted_address,
                            location: item.geometry.location
                        }
                    }));
                })
            },
            select: function(event, ui) {
                marker.setPosition(ui.item.location);
                savePosition_%(functionName)s(ui.item.location, ui.item.value);
            }
        });
    }

    $(document).ready(function(){
        load_%(functionName)s();
    });

//]]>
</script>
        ''' % dict(functionName=name.replace('-', '_'), name=name, lat=lat, lng=lng, defAddress=DEFAULT_ADDRESS)
        html = self.inner_widget.render("%s" % name, "%s" % curLocation, dict(id='id_%s' % name))
        html += '<div id="map_%s" style="width: %dpx; height: %dpx"></div>' % (name, self.map_width, self.map_height)
        html += '<h3>%s: </h3><input id="address_%s" type="text" size="50"/>' % (u'Поиск по адресу', name)
        html += '<p><h3>%s: </h3><span>%s</span></p>' % (u'Текущий адрес', address)

        return mark_safe(js + html)

    class Media:
        css = {'all': (
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/themes/redmond/jquery-ui.css',
            #'/media/css/default.css',
        )}
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js',
            'http://maps.google.com/maps/api/js?sensor=false',
        )

class LocationField(JSONField):
    def formfield(self, **kwargs):
        defaults = {'widget': LocationWidget}
        return super(LocationField, self).formfield(**defaults)

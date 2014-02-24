var request = require('request');

var queryString = ("http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-Tog'");
var queryStations = ("http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode eq 'DK'");

var main = function () {
	request({
			url: queryString,
			json: true
		},
		function (error, response, body) {
			console.log(body);
		});
};

if(require.main === module) {
	main();
}
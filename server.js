var request = require('request');

var queryString = ("http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-Tog' and TrainType ne 'S-tog'");
var queryStations = ("http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode eq '86'");

var main = function () {
	request({
			url: queryStations,
			json: true
		},
		function (error, response, body) {
			console.log(body);
		});
};

if(require.main === module) {
	main();
}
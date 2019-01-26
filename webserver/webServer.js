'use strict';
var isAuthRequired = false


/*
 * --------------------
 * Parameters
 * --------------------
 */
var serverIP = 'localhost';
var portno = 3000;
var cassIP = ['localhost:9042'];
var cassKeyspace = 'bridge_monitoring';


/*
 * --------------------
 * Import modules
 * --------------------
 */
var session = require('express-session');
var express = require('express');
var cassandra = require('cassandra-driver');
var bodyParser = require('body-parser');
var pythonShell = require('python-shell');
var uuid = require('uuid');
var fs = require('fs');
var xml = require('xml');
var xml2js = require('xml2js');
var async = require('async');
var mime = require('mime');
var dateFormat = require('dateformat');


/*
 * --------------------
 * Express module
 * --------------------
 */
var app = express();
app.use(express.static(__dirname));
app.use(session({secret: 'secretKey', resave: false, saveUninitialized: false}));
var jsonParser = bodyParser.json({limit:1024*1024*20, type:'application/json'});
var urlencodedParser = bodyParser.urlencoded({ extended:true, limit:1024*1024*20, type:'application/x-www-form-urlencoding' });
app.use(jsonParser);
app.use(urlencodedParser);


/*
 * --------------------
 * Cassandra module
 * --------------------
 */
// const authProvider = new cassandra.auth.PlainTextAuthProvider(process.argv[2], process.argv[3]);
// const cassClient = new cassandra.Client({ contactPoints: cassIP, keyspace: cassKeyspace, authProvider: authProvider});
const cassClient = new cassandra.Client({ contactPoints: cassIP, keyspace: cassKeyspace});


/*
 * --------------------
 * Run Server
 * --------------------
 */
var server = app.listen(portno, function () {
  var port = server.address().port;
  console.log('Listening at http://' + serverIP + ':' + port + ' exporting the directory ' + __dirname);
});


/*
 * --------------------------------
 * RESTful server-side data sources
 * --------------------------------
 */
app.get('/', function (request, response) {
    response.send('Simple web server of files from ' + __dirname);
});


/* 
 * --------------------
 * GET: /sensordata
 * --------------------
 */ 
const sensordataIDQuery = ['event_time_begin','event_time_end'];
app.get('/sensordata/:id', function (request, response) {
	// Check auth
	if (isAuthRequired && request.session.user_id === undefined) {
        response.status(401).end();
        return;
    };
    // Record request URL
	var url = request.protocol + '://' + request.get('host') + request.originalUrl;
	// Prepare cql query statement
	var cassQueryStmt = 'SELECT sensor_id, event_time, data FROM sensordataraw WHERE ';
	var cassQueryVal = [];
	var queryCond = [];
	queryCond.push('sensor_id = ?');
	cassQueryVal.push(request.params.id);
	// Check required query parameters
	for (k in sensordataIDQuery) {
		if (k in request.query) {
	        response.writeHead(400, {'Content-Type': 'text/plain'});
	        response.end('ERROR: Required query is omitted (' + k + ')');
	        return;
		} 
	};
	// Check unexpected query parameters
	for (var k in request.query) {
		if (sensordataIDQuery.indexOf(k) <= -1) {
	        response.writeHead(400, {'Content-Type': 'text/plain'});
	        response.end('ERROR: Unknown query parameter (' + k + ')');
	        return;
		} 
	};
	queryCond.push('event_time >= ?');
	queryCond.push('event_time <= ?');
	queryCond.push('year IN ?');
	cassQueryStmt += queryCond.join(' AND ');
	// Prepare query parameter values
	var beginDate = new Date(Date.parse(request.query['event_time_begin']));
	var endDate = new Date(Date.parse(request.query['event_time_end']));
	cassQueryVal.push(beginDate);
	cassQueryVal.push(endDate);
    var years = [];
    for (var y = beginDate.getFullYear(); y <= endDate.getFullYear(); y++) {
        years.push(y.toString());
    };
	cassQueryVal.push(years);
	// Bind query statement and query parameter values
	// Send query to Cassandra database
	var results = [];
	const options = { prepare : true , fetchSize : 5000 };
	cassClient.execute(cassQueryStmt, cassQueryVal, function(err, result) {
		if (err) {
			console.log(err);
            response.status(400).send(JSON.stringify(err));
		} else {
			// console.log('Success (' + new Date() + '): GET /sensordata/:id [Query: ' + cassQueryStmt +']')
			console.log(result.rows);
			response.status(200).send(JSON.stringify({"content":result.rows, "links":[{"rel": "self","href": url}]}));
		}
		return;
	});
});


/*
 * --------------------
 * POST: /sensordata
 * --------------------
 */ 
app.post('/sensordata', function (request, response) {   
	// Check auth
	if (isAuthRequired && request.session.user_id === undefined) {
        response.status(401).end();
        return;
    }
    // Parse incoming data
	var body = JSON.parse(JSON.stringify(request.body));
	// Prepare cql query statement
	const query = 'INSERT INTO sensordataraw (sensor_id, year, event_time, data) values (?, ?, ?, ?)';
	// Bind query statement and query parameter values
	var queries = []
	for (var i=0; i<body.length; i++){
		var ts = new Date(Date.parse(body[i].event_time));
		var params = [body[i].sensor_id, (dateFormat(ts, "yyyy")), ts, body[i].data];
		queries.push({'query':query, 'params':params});
	}
	// Send query to Cassandra database
	cassClient.batch(queries, { prepare: true }, function (err) {
   		if (err) {
            response.status(400).end();
		} else {
			response.status(200).end();
		}
		return;
	});
});


/* 
 * --------------------
 * GET: /sensor
 * --------------------
 */ 
const sensorQuery = ['sensorType', 'install', 'remove'];
app.get('/sensor', function (request, response) {
	// Check auth
	if (isAuthRequired && request.session.user_id === undefined) {
        response.status(401).end();
        return;
    }
    // Record request URL
	var url = request.protocol + '://' + request.get('host') + request.originalUrl;
	// Prepare cql query statement
	var cassQueryStmt = 'SELECT * FROM sensor WHERE ';
	var cassQueryVal = [];
	var queryCond = [];
	// Check unexpected query parameters
	for (var k in request.query) {
		if (sensorQuery.indexOf(k) <= -1) {
	        response.writeHead(400, {'Content-Type': 'text/plain'});
	        response.end('ERROR: Unknown query parameter (' + k + ')');
	        return;
		} else {
			// Push sensorType and install to the query statement
			if (k == 'sensorType') {
				queryCond.push('sensor_type = ?');
				cassQueryVal.push(request.query[k]);
			} else if (k == 'install') {
				queryCond.push('install <= ?');
				cassQueryVal.push(new Date(Date.parse(request.query[k])));
			}
		}
	}
	// Push remove to the query statement. If there's no remove query input, use default.
	queryCond.push('remove >= ?');
	if ('remove' in request.query) {
		cassQueryVal.push(new Date(Date.parse(request.query['remove'])));	
	} else {
		cassQueryVal.push(new Date());
	}
	// Check if install is earlier than removal.
	if (new Date(Date.parse(request.query['install'])) >= cassQueryVal[cassQueryVal.length-1]) {
        response.writeHead(400, {'Content-Type': 'text/plain'});
        response.end('ERROR: Wrong query condition. (install should be earlier than remove.)');
        return;
	}
	cassQueryStmt += queryCond.join(' AND ');
	cassQueryStmt += ' ALLOW FILTERING;'
	// Send query to Cassandra database
	cassClient.execute(cassQueryStmt, cassQueryVal, function(err, result) {
		if (err) {
			console.log(err)
            response.status(400).send(JSON.stringify(err));
		} else {
			response.status(200).send(JSON.stringify({"content":result.rows, "links":[{"rel": "self","href": url}]}));
		}
		return;
	});
});



/* 
 * --------------------
 * GET: /sensor/:id
 * --------------------
 */ 
const sensorIDQuery = ['property', 'install', 'remove'];
app.get('/sensor/:id', function (request, response) {
	// Check auth
	if (isAuthRequired && request.session.user_id === undefined) {
        response.status(401).end();
        return;
    }
    // Record request URL
	var url = request.protocol + '://' + request.get('host') + request.originalUrl;
	// Prepare cql query statement
	var cassQueryStmt = 'SELECT '
	if ('property' in request.query) {
		cassQueryStmt += request.query['property'];
	} else {
		cassQueryStmt += '*';
	}
	cassQueryStmt += ' FROM sensor WHERE ';
	var cassQueryVal = [];
	var queryCond = [];
	queryCond.push('sensor_id = ?');
	cassQueryVal.push(request.params.id);
	// Check unexpected query condition
	for (var k in request.query) {
		if (sensorIDQuery.indexOf(k) <= -1) {
	        response.writeHead(400, {'Content-Type': 'text/plain'});
	        response.end('ERROR: Unknown query parameter (' + k + ')');
	        return;
		} else {
			// Push install to the query statement
			 if (k == 'install') {
				queryCond.push('install <= ?');
				cassQueryVal.push(new Date(Date.parse(request.query[k])));
			}
		}
	}
	// Push remove to the query statement. If there's no remove query input, use default.
	queryCond.push('remove >= ?');
	if ('remove' in request.query) {
		cassQueryVal.push(new Date(Date.parse(request.query['remove'])));	
	} else {
		cassQueryVal.push(new Date());
	}
	// Check if install is earlier than removal.
	if (new Date(Date.parse(request.query['install'])) >= cassQueryVal[cassQueryVal.length-1]) {
        response.writeHead(400, {'Content-Type': 'text/plain'});
        response.end('ERROR: Wrong query condition. (install should be earlier than remove.)');
        return;
	}
	cassQueryStmt += queryCond.join(' AND ');
	cassQueryStmt += ' ALLOW FILTERING;'
	// Send query to Cassandra database
	cassClient.execute(cassQueryStmt, cassQueryVal, function(err, result) {
		if (err) {
            response.status(400).send(JSON.stringify(err));
		} else {
			// console.log('Success (' + new Date() + '): GET /sensor/:id [Query: ' + cassQueryStmt +']')
			response.status(200).send(JSON.stringify({"content":[result.rows[0]], "links":[{"rel": "self","href": url}]}));
		}
		return;
	});
});


/* 
 * --------------------
 * POST: /sensor
 * --------------------
 */ 
app.post('/sensor', function (request, response) {
	// Check auth
	if (isAuthRequired && request.session.user_id === undefined) {
        response.status(401).end();
        return;
    };
    // Parse incoming data
	var body = JSON.parse(JSON.stringify(request.body));
	var keys = [];
	var values = [];
	var questions = [];
	for (var k in body) {
		keys.push(k);
		if (k === "install" || k === "remove") {
			values.push(new Date(Date.parse(body[k])));
		} else {
			values.push(body[k]);
		}
		questions.push("?")
	};
	// Create query statement
	var query = 'INSERT INTO sensor (' + keys.join(', ') + ') values (' + questions.join(', ') + ')';
	// Send query to Cassandra database
	cassClient.execute(query, values, function(err, result) {
		if (err) {
			console.log(err);
            response.status(400).end();
		} else {
			response.status(200).end();
		}
		return;
	});
});



// /* 
//  * --------------------
//  * GET: /imagedata/:id
//  * --------------------
//  */ 
// const imagedataIDQuery = ['date','event_time_begin','event_time_end'];
// app.get('/imagedata/:id', function (request, response) {
// 	if (isAuthRequired && request.session.user_id === undefined) {
//         response.status(401).end();
//         return;
//     }

// 	var url = request.protocol + '://' + request.get('host') + request.originalUrl;

// 	var cassQueryStmt = 'SELECT camera_id, event_time, image FROM imagedata WHERE ';
// 	var cassQueryVal = [];
// 	var queryCond = [];
// 	queryCond.push('camera_id = ?');
// 	cassQueryVal.push(request.params.id);

// 	for (k in imagedataIDQuery) {
// 		if (k in request.query) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Required query is omitted (' + k + ')');
// 	        return;
// 		} 
// 	};

// 	// Check if there're unexpected query condition
// 	for (var k in request.query) {
// 		if (imagedataIDQuery.indexOf(k) <= -1) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Unknown query parameter (' + k + ')');
// 	        return;
// 		} 
// 	};

// 	var beginDate = new Date(Date.parse(request.query['event_time_begin']))
// 	var endDate = new Date(Date.parse(request.query['event_time_end']))

// 	queryCond.push('event_time >= ?');
// 	cassQueryVal.push(beginDate);
// 	queryCond.push('event_time <= ?');
// 	cassQueryVal.push(endDate);

// 	var month = [];
// 	var m = new Date(beginDate);
// 	m.setDate(1);

// 	while (m <= endDate) {
// 		month.push(dateFormat(m, "yyyymm"));
// 		m.setMonth(m.getMonth() + 1);
// 	};

// 	queryCond.push('month IN ?');
// 	cassQueryVal.push(month);

// 	// Build query statement
// 	cassQueryStmt += queryCond.join(' AND ');

// 	// Execute query 
// 	cassClient.execute(cassQueryStmt, cassQueryVal, function(err, result) {
// 		if (err) {
//             response.status(400).send(JSON.stringify(err));
// 		} else {
// 			console.log('Success (' + new Date() + '): GET /sensordata/:id [Query: ' + cassQueryStmt +']')
// 			response.status(200).send(JSON.stringify({"content":result.rows, "links":[{"rel": "self","href": url}]}));
// 		}
// 		return;
// 	});
// });



// /* 
//  * --------------------
//  * POST: /imagedata
//  * --------------------
//  */ 

// app.post('/imagedata', function (request, response) {   
// 	if (isAuthRequired && request.session.user_id === undefined) {
//         response.status(401).end();
//         return;
//     }

// 	var body = JSON.parse(JSON.stringify(request.body))
// 	const query = 'INSERT INTO imagedata (camera_id, month, event_time, image) values (?, ?, ?, ?)';
// 	var queries = [];
// 	for (var i=0; i<body.length; i++){
// 		var ts = new Date(Date.parse(body[i].event_time));
// 		var buf = new Buffer(body[i].data, 'base64');
// 		var params = [body[i].camera_id, dateFormat(ts, "yyyymm"), ts, buf];
// 		queries.push({'query':query, 'params':params});
// 	};

// 	cassClient.batch(queries, { prepare: true }, function (err) {
//    		if (err) {
//             response.status(400).end();
// 		} else {
// 			response.status(200).end();
// 		}
// 		return;
// 	});
// });



// /* 
//  * --------------------
//  * GET: /weatherdata
//  * --------------------
//  */ 
// const weatherdataIDQuery = ['event_time_begin','event_time_end'];
// app.get('/weatherdata/:state/:city', function (request, response) {
// 	if (isAuthRequired && request.session.user_id === undefined) {
//         response.status(401).end();
//         return;
//     }

// 	var url = request.protocol + '://' + request.get('host') + request.originalUrl;

// 	var cassQueryStmt = 'SELECT * FROM weatherdata WHERE ';
// 	var cassQueryVal = [];
// 	var queryCond = [];
// 	queryCond.push('state = ?');
// 	cassQueryVal.push(request.params.state);
// 	queryCond.push('city = ?');
// 	cassQueryVal.push(request.params.city);

// 	for (k in weatherdataIDQuery) {
// 		if (k in request.query) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Required query is omitted (' + k + ')');
// 	        return;
// 		} 
// 	};

// 	// Check if there're unexpected query condition
// 	for (var k in request.query) {
// 		if (weatherdataIDQuery.indexOf(k) <= -1) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Unknown query parameter (' + k + ')');
// 	        return;
// 		} 
// 	};

// 	var beginDate = new Date(Date.parse(request.query['event_time_begin']));
// 	var endDate = new Date(Date.parse(request.query['event_time_end']));

// 	queryCond.push('event_time >= ?');
// 	cassQueryVal.push(beginDate);
// 	queryCond.push('event_time <= ?');
// 	cassQueryVal.push(endDate);

// 	// Build query statement
// 	cassQueryStmt += queryCond.join(' AND ');

// 	console.log(cassQueryStmt)
// 	console.log(cassQueryVal)

// 	// Execute query 
// 	cassClient.execute(cassQueryStmt, cassQueryVal, function(err, result) {
// 		if (err) {
// 			console.log(err)
//             response.status(400).send(JSON.stringify(err));
// 		} else {
// 			response.status(200).send(JSON.stringify({"content":result.rows, "links":[{"rel": "self","href": url}]}));
// 		}
// 		return;
// 	});
// });



// /*
//  * --------------------
//  * POST: /weatherdata
//  * --------------------
//  */ 
// app.post('/weatherdata', function (request, response) {   
// 	/* AUTH */
// 	if (isAuthRequired && request.session.user_id === undefined) {
//         response.status(401).end();
//         return;
//     }
//     var body = JSON.parse(JSON.stringify(request.body));
// 	var queries = [];
// 	for (var i=0; i<body.length; i++){	
// 		var keys = [];
// 		var values = [];
// 		var questions = [];
// 		for (var k in body[i]) {
// 			keys.push(k)
// 			values.push(body[i][k])
// 			questions.push("?")
// 		};
// 		var query = 'INSERT INTO weatherdata (' + keys.join(', ') + ') values (' + questions.join(', ') + ')'
// 		queries.push({'query':query, 'params':values});
// 	}

// 	cassClient.batch(queries, { prepare: true }, function (err) {
//    		if (err) {
//    			console.log(err)
//             response.status(400).end();
// 		} else {
// 			response.status(200).end();
// 		}
// 		return;
// 	});
// });



// /* 
//  * --------------------
//  * POST: /admin/login
//  * --------------------
//  */ 
// app.post('/admin/login', function (request, response) {  
// 	const query = 'SELECT * FROM userlist WHERE user_id = ?';
// 	// Execute query 
// 	cassClient.execute(query, [request.body["user_id"]], function(err, result) {
// 		if (err) {
// 			console.log(err);
//             response.status(400).send(JSON.stringify(err));
// 		} else {
// 			if (result.rows.length === 0 ){
//         		response.status(400).send(JSON.stringify(err));
//             	return;
// 			};
// 			var userInfo = result.rows[0];
// 	        if (userInfo["password"] !== request.body.password) {
// 			    response.status(400).send("Wrong Password");
// 			    return;
// 			}
// 			request.session.user_id = userInfo.user_id;
// 			request.session.first_name = userInfo.first_name;
// 			request.session.last_name = userInfo.last_name;
// 			response.status(200).end();
// 		}
// 		return;
// 	});
// });



// /* 
//  * --------------------
//  * POST: /admin/logout
//  * --------------------
//  */ 
// app.post('/admin/logout', function (request, response) {    
//     if (request.session.user_id === undefined) {
//         response.status(400).end();
//         return;
//     }
// 	delete request.session.user_id;
//     delete request.session.first_name;
//     delete request.session.last_name;
//     request.session.destroy(function(err) {
//         if (err) {
//             console.log(err);
//             response.status(400).send(JSON.stringify(err));
//             return;
//         }
//         response.status(200).end();
//     });   
// });



// /* ****************
//  * GET: /daqevent
//  * ****************
//  */ 
// const daqeventQuery = ['event_time_begin','event_time_end'];
// app.get('/daqevent', function (request, response) {
// 	var url = request.protocol + '://' + request.get('host') + request.originalUrl;

// 	var cassQueryStmt = 'SELECT event_time, sensor FROM daqevent ';
// 	var cassQueryVal = [];
// 	var queryCond = [];

// 	if (Object.keys(request.query).length != 0) {
// 		cassQueryStmt += 'WHERE ';
// 		// Check if there're unexpected query condition
// 		for (var k in request.query) {
// 			if (daqeventQuery.indexOf(k) <= -1) {
// 		        response.writeHead(400, {'Content-Type': 'text/plain'});
// 		        response.end('ERROR: Unknown query parameter (' + k + ')');
// 		        return;
// 			} else {
// 				// Push event_time_begin, event_time_end to the query statement
// 				if (k == 'event_time_begin') {
// 					queryCond.push('event_time >= ?');
// 					cassQueryVal.push(new Date(Date.parse(request.query[k])));
// 				} else if (k == 'event_time_end') {
// 					queryCond.push('event_time <= ?');
// 					cassQueryVal.push(new Date(Date.parse(request.query[k])));
// 				}
// 			}
// 		}
		
// 		// Check if install is earlier than removal.
// 		if (new Date(Date.parse(request.query['event_time_begin'])) >= new Date(Date.parse(request.query['event_time_end'])) ) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Wrong query condition. (event_time_begin should be earlier than event_time_end.)');
// 	        return;
// 		}

// 		// Build query statement
// 		cassQueryStmt += queryCond.join(' AND ');
// 		cassQueryStmt += ' ALLOW FILTERING;'
// 	}

// 	// Execute query 
// 	cassClient.execute(cassQueryStmt, cassQueryVal, function(err, result) {
// 		if (err) {
//             response.status(400).send(JSON.stringify(err));
// 		} else {
// 			console.log('Success (' + new Date() + '): GET /sensordata [Query: ' + cassQueryStmt +']')
// 			response.status(200).send(JSON.stringify({"content":result.rows, "links":[{"rel": "self","href": url}]}));
// 		}
// 		return;
// 	});
// });



// /* *************
//  * GET: /femodel
//  * *************
//  */ 
// const femodelQuery = ['format'];
// const femodelFormat = ['xlsx', 'xml']
// app.get('/femodel/:id', function (request, response) {
// 	// var options = {mode: 'text', pythonOptions: ['-u'], args: []};
// 	for (var k in request.query) {
// 		if (femodelQuery.indexOf(k) <= -1) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Unknown query parameter (' + k + ')');
// 	        return;
// 		}
// 	}
// 	if ('format' in request.query) {
// 		if (femodelFormat.indexOf(request.query['format']) <= -1) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Unknown format type (' + request.query['format'] + ')');
// 	        return;			
// 		}
// 	}
// 	if (request.params.id != 'trb') {
//         response.writeHead(400, {'Content-Type': 'text/plain'});
//         response.end('ERROR: Unknown bridge id (' + request.params.id + ')');
//         return;
// 	}
// 	PythonShell.run('brim_lib/cass_to_brimfem.py', function (err, result) {
// 		if (err) {
// 			response.status(400).send(JSON.stringify(err));
// 		} else {
// 			if (!('format' in request.query)) {
// 				console.log('Success (' + new Date() + '): GET /femodel [Run Python Script: brim_lib/cass_to_brimfem.py]')
// 				response.status(200).sendfile(result[0]);
// 			} else {
// 				if (request.query['format'] == 'xml') {
// 					console.log('Success (' + new Date() + '): GET /femodel [Run Python Script: brim_lib/cass_to_brimfem.py]')
// 					response.status(200).sendfile(result[0]);
// 				} else {
// 					PythonShell.run('brim_lib/brimfem_to_csi.py', function (err, result) {
// 						if (err) {
// 							response.status(400).send(JSON.stringify(err));
// 						} else {
// 							var filename = result[0];
//   							var mimetype = mime.lookup(filename);
//   							response.setHeader('Content-disposition', 'attachment; filename=' + filename);
//   							response.setHeader('Content-type', mimetype);
//   							// var filestream = fs.createReadStream(filename);
//   							// filestream.pipe(response);
// 							console.log('Success (' + new Date() + '): GET /femodel [Run Python Script: brim_lib/brimfem_to_csi.py]')
// 							response.status(200).sendfile(result[0]);
// 						}
// 					});
// 				}
// 			}
// 		}
// 		return;
// 	});
// });

// /* ********************
//  * GET: /geometricmodel
//  * ********************
//  */ 
// const geometricmodelQuery = [];
// app.get('/geometricmodel/:id', function (request, response) {
// 	// var options = {mode: 'text', pythonOptions: ['-u'], args: []};
// 	for (var k in request.query) {
// 		if (geometricmodelQuery.indexOf(k) <= -1) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Unknown query parameter (' + k + ')');
// 	        return;
// 		}
// 	}
// 	if (request.params.id != 'trb') {
//         response.writeHead(400, {'Content-Type': 'text/plain'});
//         response.end('ERROR: Unknown bridge id (' + request.params.id + ')');
//         return;
// 	}
// 	PythonShell.run('brim_lib/cass_to_brimgeo.py', function (err, result) {
// 		if (err) {
// 			response.status(400).send(JSON.stringify(err));
// 		} else {
// 			console.log('Success (' + new Date() + '): GET /geometricmodel [Run Python Script: brim_lib/cass_to_brimgeo.py]')
// 			response.status(200).sendfile(result[0]);
// 		}
// 		return;
// 	});
// });


// /* **********
//  * GET: /wadl
//  * **********
//  */ 
// app.get('/wadl', function (request, response) {
// 	for (var k in request.query) {
// 		if (geometricmodelQuery.indexOf(k) <= -1) {
// 	        response.writeHead(400, {'Content-Type': 'text/plain'});
// 	        response.end('ERROR: Unknown query parameter (' + k + ')');
// 	        return;
// 		}
// 	}
// 	console.log('Success (' + new Date() + '): GET /wadl ')
// 	response.status(200).sendfile('wadl/application.wadl');
// 	return;
// });


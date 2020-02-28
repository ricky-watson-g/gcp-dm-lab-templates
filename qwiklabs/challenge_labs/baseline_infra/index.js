/* globals exports, require */
//jshint strict: false
//jshint esversion: 6
"use strict";
const crc32 = require("fast-crc32c");
const gcs = require("@google-cloud/storage")();
const imagemagick = require("imagemagick-stream");

exports.thumbnail = (event, context) => {
    const fileName = event.name;
    const bucketName = event.bucket;
  	const size = "64x64"
 	const bucket = gcs.bucket(bucketName);
  	if ( fileName.search("64x64_thumbnail") == -1 ){
      // doesn't have a thumbnail, get the filename extention
      var filename_split = fileName.split('.');
      var filename_ext = filename_split[filename_split.length - 1];
      var filename_without_ext = fileName.substring(0, fileName.length - filename_ext.length );
      if (filename_ext.toLowerCase() == 'png' || filename_ext.toLowerCase() == 'jpg'){
        // only support png and jpg at this point
        console.log(`Processing Original: gs://${bucketName}/${fileName}`);
        const gcsObject = bucket.file(fileName);
        let newFilename = filename_without_ext + size + '_thumbnail.' + filename_ext;
        let gcsNewObject = bucket.file(newFilename);
        let srcStream = gcsObject.createReadStream();
        let dstStream = gcsNewObject.createWriteStream();
        let resize = imagemagick().resize(size).quality(90);
        console.log("Pipe");
        srcStream.pipe(resize).pipe(dstStream);
        return new Promise((resolve, reject) => {
            dstStream
            .on("error", (err) => {
                console.log(`Error: ${err}`);
                reject(err);
            })
            .on("finish", () => {
                console.log(`Success: ${fileName} → ${newFilename}`);
                // set the content-type
                gcsNewObject.setMetadata(
                  {
                    contentType: 'image/'+ filename_ext.toLowerCase()
                  }, function(err, apiResponse) {});
                resolve();
            });
        });
      }
      else {
	  	console.log(`gs://${bucketName}/${fileName} is not an image I can handle`);
      }
    }
    else {
      console.log(`gs://${bucketName}/${fileName} already has a thumbnail`);
    }
};
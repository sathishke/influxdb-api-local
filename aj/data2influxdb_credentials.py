# Source: https://github.com/fabio-miranda/csv-to-influxdb


@@ -36,9 +36,7 @@ def loadCsv(inputfilename, servername, user, password, dbname, metric, timecolum
    with open(inputfilename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            name = metric
            timestamp = unix_time_millis(datetime.datetime.strptime(row[timecolumn],timeformat)) * 1000000 # in nanoseconds
            value = float(row[metric])

            tags = {}
            for t in tagcolumns:
@@ -51,36 +49,46 @@ def loadCsv(inputfilename, servername, user, password, dbname, metric, timecolum
            for f in fieldcolumns:
                v = 0
                if f in row:
                    v = row[f]
                    v = float(row[f])
                fields[f] = v


            point = {"measurement": metric, "time": timestamp, "fields": fields, "tags": tags}

            datapoints.append(point)

            if count % batchsize == 0:
                print 'Read %d lines'%count
            count+=1

            if len(datapoints) % batchsize == 0:
                print 'Read %d lines'%count
                print 'Inserting %d datapoints...'%(len(datapoints))
                response = client.write_points(datapoints)

                if response == False:
                    print 'Problem inserting points, exiting...'
                    exit(1)

                print "Wrote %d, response: %s" % (len(datapoints), response)


    start = 0
    end = min(count, batchsize)
    while start < count:
                datapoints = []


        data = datapoints[start:end]
    # write rest
    if len(datapoints) > 0:
        print 'Read %d lines'%count
        print 'Inserting %d datapoints...'%(len(datapoints))
        response = client.write_points(datapoints)

        # insert
        print 'Inserting datapoints...'
        response = client.write_points(data)
        if response == False:
            print 'Problem inserting points, exiting...'
            exit(1)

        print "Wrote %d, response: %s" % (end-start, response)
        print start, end
        print "Wrote %d, response: %s" % (len(datapoints), response)

        start += batchsize
        end = min(count, end+batchsize)
    print 'Done'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Csv to kairodb.')
    parser = argparse.ArgumentParser(description='Csv to influxdb.')

    parser.add_argument('-i', '--input', nargs='?', required=True,
                        help='Input csv file.')
@@ -116,7 +124,7 @@ def loadCsv(inputfilename, servername, user, password, dbname, metric, timecolum
                        help='List of csv columns to use as tags, separated by comma, e.g.: host,data_center. Default: host')

    parser.add_argument('-g', '--gzip', action='store_true', default=False,
                        help='Compress before sending to kairodb.')
                        help='Compress before sending to influxdb.')

    parser.add_argument('-b', '--batchsize', type=int, default=5000,
                        help='Batch size. Default: 5000.')

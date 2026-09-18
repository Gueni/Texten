import assets.Dependencies as dp
import Lib.Data_Process as pp

import Lib.io.Reader as Reader
import Lib.io.Writer as Writer

InputContext = Reader.InputContext()
outputContext = Writer.OutputContext()

reader = Reader.CSVReader()
readerHeader = Reader.CSVReaderHeader()
writer = Writer.CSVWriter()

path = "enter path to first time series file without .csv"

logPath = "enter path to CSV_TIME_SERIES folder"

InputContext.rawDataPath = path

postProcessing = pp.Processing()

ppRes = postProcessing.gen_result(logPath,0,"enter utc nuber from result")

reader.read(InputContext)
readerHeader.read(InputContext)

#print(simContext.data)
print(InputContext.header)
print(InputContext.headerLen)

#print(ppRes)
print(dp.std_headers)
print(dp.std_length)

outputContext.path = "Script/Tests/testdata"
outputContext.data = InputContext.data

writer.write(outputContext)

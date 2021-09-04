import matplotlib.pyplot as plt
import pandas as pd
import os


def setParams(tcpMethod, cwnd, rtt, goodput, tcpConnectionNum):
    variablesInfo = pd.read_csv(tcpMethod + "VariableTrace" + str(tcpConnectionNum) + ".tr", sep="\t")
    cwndColumnList = list(variablesInfo["cwnd"])
    rttColumnList = list(variablesInfo["rtt"])
    goodputColumnList = list(variablesInfo["goodput"])
    for i in range(len(cwnd)):
        cwnd[i] += cwndColumnList[i]
        rtt[i] += rttColumnList[i]
        goodput[i] += goodputColumnList[i]


def setDrops(tcpMethod, drops1, drops2):
    packetsInfo = pd.read_csv(tcpMethod + "PacketTrace.tr", sep=" ")
    packetsInfo.columns = ["event", "time", "sending", "receiving", "protocol", "size", "flags", "fid", "src", "dst", "sequence Number", "packetId"]
    allDrops = packetsInfo.loc[packetsInfo["event"] == "d"]
    drops1TimeList = list(allDrops.loc[packetsInfo["fid"] == 1]["time"])
    drops2TimeList = list(allDrops.loc[packetsInfo["fid"] == 2]["time"])

    for i in range(len(drops1TimeList)):
        if drops1TimeList[i] < 1000:
            drops1[int(drops1TimeList[i])] += 1

    for i in range(len(drops2TimeList)):
        if drops2TimeList[i] < 1000:
            drops2[int(drops2TimeList[i])] += 1


def moveFilesToProperSimulationFolder(tcpMethod):
    os.system("mv *.tr *.nam " + tcpMethod + "\ Files")


def getAgentType(tcpMethod):
    return "TCP" + (("/" + tcpMethod) if tcpMethod != "Tahoe" else "")


def createSimulationFolder(tcpMethod):
    os.system("rm -rf " + tcpMethod + "\ Files")
    os.mkdir(tcpMethod + " Files")


def getTcpInfo(tcpMethod):
    cwnd1, rtt1, drops1, goodput1 = [0] * 1000, [0] * 1000, [0] * 1000, [0] * 1000
    cwnd2, rtt2, drops2, goodput2 = [0] * 1000, [0] * 1000, [0] * 1000, [0] * 1000
    createSimulationFolder(tcpMethod)
    for i in range(10):
        os.system("ns NS2_TCP.tcl " + "{" + tcpMethod + "} {" + getAgentType(tcpMethod) + "}")
        setParams(tcpMethod, cwnd1, rtt1, goodput1, 1)
        setParams(tcpMethod, cwnd2, rtt2, goodput2, 2)
        setDrops(tcpMethod, drops1, drops2)
        moveFilesToProperSimulationFolder(tcpMethod)

    for i in range(1000):
        cwnd1[i] /= 10
        rtt1[i] /= 10
        drops1[i] /= 10
        goodput1[i] /= 10
        cwnd2[i] /= 10
        rtt2[i] /= 10
        drops2[i] /= 10
        goodput2[i] /= 10

    return [[cwnd1, rtt1, drops1, goodput1], [cwnd2, rtt2, drops2, goodput2]]


def savePLotInfoInFile(newrenoInfo, tahoeInfo, vegasInfo, infoName):
    data = {
        "Newreno " + infoName + " flow 1": newrenoInfo[0],
        "Newreno " + infoName + " flow 2": newrenoInfo[1],
        "Tahoe " + infoName + " flow 1": tahoeInfo[0],
        "Tahoe " + infoName + " flow 2": tahoeInfo[1],
        "Vegas " + infoName + " flow 1": vegasInfo[0],
        "Vegas " + infoName + " flow 2": vegasInfo[1]
    }
    pd.DataFrame(data=data).to_csv("./plots/" + infoName + "PlotInfo.csv", index=False)


def drawSeparately(infoData, infoName, tcpMethod):
    plt.figure(figsize=(12, 5))
    plt.plot(infoData[0], color="red")
    plt.plot(infoData[1], color="blue")
    plt.legend([tcpMethod + " Flow1 ", tcpMethod + " Flow2 "])
    plt.xlabel("time")
    plt.ylabel(infoName + "(" + getUnit(infoName) + ")")
    plt.title(infoName)
    plt.savefig("./plots/" + infoName + "-" + tcpMethod)


def drawEachMethodSeparately(newrenoInfo, tahoeInfo, vegasInfo, infoName):
    drawSeparately(newrenoInfo, infoName, "Newreno")
    drawSeparately(tahoeInfo, infoName, "Tahoe")
    drawSeparately(vegasInfo, infoName, "Vegas")


def getUnit(infoName):
    units = {
        "CWND": "packets",
        "Goodput": "Mb",
        "RTT": "ms",
        "Packet Loss": "packets"
    }
    return units[infoName]


def drawInfo(newrenoInfo, tahoeInfo, vegasInfo, infoName):
    savePLotInfoInFile(newrenoInfo, tahoeInfo, vegasInfo, infoName)

    plt.figure(figsize=(12, 5))
    plt.plot(newrenoInfo[0], color="red")
    plt.plot(newrenoInfo[1], color="blue")
    plt.plot(tahoeInfo[0], color="orange")
    plt.plot(tahoeInfo[1], color="green")
    plt.plot(vegasInfo[0], color="brown")
    plt.plot(vegasInfo[1], color="purple")
    plt.legend(["Newreno Flow1 ", "Newreno Flow2 ", "Tahoe Flow1 ", "Tahoe Flow1 ",
                "Vegas Flow1 ", "Vegas Flow1 "])
    plt.xlabel("Time(s)")
    plt.ylabel(infoName + "(" + getUnit(infoName) + ")")
    plt.title(infoName)
    plt.savefig("./plots/" + infoName)
    plt.show()

    # drawEachMethodSeparately(newrenoInfo, tahoeInfo, vegasInfo, infoName)


def drawPlots(newrenoInfo, tahoeInfo, vegasInfo):
    os.system("rm -rf plots")
    os.mkdir("plots")
    drawInfo([newrenoInfo[0][0], newrenoInfo[1][0]], [tahoeInfo[0][0], tahoeInfo[1][0]], [vegasInfo[0][0], vegasInfo[1][0]], "CWND")
    drawInfo([newrenoInfo[0][1], newrenoInfo[1][1]], [tahoeInfo[0][1], tahoeInfo[1][1]], [vegasInfo[0][1], vegasInfo[1][1]], "RTT")
    drawInfo([newrenoInfo[0][2], newrenoInfo[1][2]], [tahoeInfo[0][2], tahoeInfo[1][2]], [vegasInfo[0][2], vegasInfo[1][2]], "Packet Loss")
    drawInfo([newrenoInfo[0][3], newrenoInfo[1][3]], [tahoeInfo[0][3], tahoeInfo[1][3]], [vegasInfo[0][3], vegasInfo[1][3]], "Goodput")


if __name__ == "__main__":
    newrenoInfo = getTcpInfo("Newreno")
    tahoeInfo = getTcpInfo("Tahoe")
    vegasInfo = getTcpInfo("Vegas")
    drawPlots(newrenoInfo, tahoeInfo, vegasInfo)
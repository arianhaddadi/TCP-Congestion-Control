# Setting Command Line Arguments To be used as variables inside script
set protocol [expr [lindex $argv 0]]
set agentType [expr [lindex $argv 1]]


# Creating a simulator object 
set ns [new Simulator]  

# Opening the NAM trace file 
set namFile [open ${protocol}namFile.nam w] 
$ns namtrace-all $namFile 

# Opening packet trace file for tracing packets
set packetTraceFile [open ${protocol}PacketTrace.tr w]
$ns trace-all $packetTraceFile

# Opening variable trace file for TCP between node 1 and node 5
set variableTraceFile1 [open ${protocol}VariableTrace1.tr w]

# Opening variable trace file for TCP between node 2 and node 6
set variableTraceFile2 [open ${protocol}VariableTrace2.tr w]

# defining procedure for finishing simulation and closing trace files and running nam animator
proc finish {} { 
	global ns namFile packetTraceFile variableTraceFile1 variableTraceFile2 protocol
	$ns flush-trace 
	
	# Closing trace files 
	close $namFile 
	close $packetTraceFile
	close $variableTraceFile1
	close $variableTraceFile2

	# Executing nam on the nam trace file 
	# exec nam ${protocol}namFile.nam &
	exit 0
} 

# Defining procedure for generating random numbers between 5 and 25 for links with variable delay values
proc generateRandom {} {
	return [expr round(rand()*20)+5]
}

# Creating Six Nodes 
set n1 [$ns node] 
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node] 
set n5 [$ns node] 
set n6 [$ns node] 

# Creating links between the nodes 
$ns duplex-link $n1 $n3 100Mb 5ms DropTail 
$ns duplex-link $n2 $n3 100Mb [generateRandom]ms DropTail 
$ns duplex-link $n3 $n4 100Kb 1ms DropTail 
$ns duplex-link $n4 $n5 100Mb 5ms DropTail 
$ns duplex-link $n4 $n6 100Mb [generateRandom]ms DropTail 

# Setting queue size for routers
$ns queue-limit $n3 $n1 10
$ns queue-limit $n3 $n2 10
$ns queue-limit $n3 $n4 10

$ns queue-limit $n4 $n3 10
$ns queue-limit $n4 $n5 10
$ns queue-limit $n4 $n6 10

# Setting nodes positions (for NAM)
$ns duplex-link-op $n1 $n3 orient right-down 
$ns duplex-link-op $n2 $n3 orient right-up 
$ns duplex-link-op $n3 $n4 orient right 
$ns duplex-link-op $n4 $n5 orient right-up 
$ns duplex-link-op $n4 $n6 orient right-down 

# Monitoring the queue for links (for NAM)
$ns duplex-link-op $n3 $n4 queuePos 0.5
$ns duplex-link-op $n4 $n5 queuePos 0.5
$ns duplex-link-op $n4 $n6 queuePos 0.5

# Setting Up Connection Between Node 1 and Node 5
# Setting Up TCP Agent for Node 1
set tcp1 [new Agent/$agentType] 
$tcp1 set class_ 1
$tcp1 set fid_ 1
$tcp1 set ttl_ 64
$ns color 1 Blue 
$ns attach-agent $n1 $tcp1 


# Setting Up Sink for Node 5
set sink5 [new Agent/TCPSink] 
$ns attach-agent $n5 $sink5 

# Connecting Node 1 and Node 5
$ns connect $tcp1 $sink5 

# Setting Up FTP for TCP Connection Between Node 1 and Node 5
set ftp1 [new Application/FTP] 
$ftp1 attach-agent $tcp1 
$ftp1 set type_ FTP 


# Setting Up Connection Between Node 2 and Node 6
# Seeting Up TCP Agent for Node 2
set tcp2 [new Agent/$agentType]  
$tcp2 set class_ 2
$tcp2 set fid_ 2
$tcp2 set ttl_ 64
$ns color 2 Red
$ns attach-agent $n2 $tcp2 

# Setting Up Sink for Node 6
set sink6 [new Agent/TCPSink] 
$ns attach-agent $n6 $sink6 

# Setting Up FTP for TCP Connection Between Node 2 and Node 6
set ftp2 [new Application/FTP] 
$ftp2 attach-agent $tcp2 
$ftp2 set type_ FTP 

# Connecting Node 2 and Node 6
$ns connect $tcp2 $sink6 

# Schedule running for FTP 
$ns at 0.0 "$ftp1 start"
$ns at 1000.0 "$ftp1 stop"
$ns at 0.0 "$ftp2 start"
$ns at 1000.0 "$ftp2 stop"


# finishing simulation procedure at time 1001 (1 time unit after stopping ftps)
$ns at 1001.0 "finish"


# Declaring class "TraceGoodput" as a child class of "Application"
Class TraceGoodput -superclass Application     

    # Overriding "init" method for class "TraceGoodput"
    TraceGoodput instproc init {args} {
        $self set bytes_ 0
        eval $self next $args
    }

    # Overriding "recv" method for class "TraceGoodput"
    TraceGoodput instproc recv {byte} {
        $self instvar bytes_
        set bytes_ [expr $bytes_ + $byte]
        return $bytes_
    }




proc writeInOutputFile {tcpSource traceGoodput outputFile} {
    global ns

    set now [$ns now]
    set cwnd [$tcpSource set cwnd_]
    set rtt [$tcpSource set rtt_]


    set nbytes [$traceGoodput set bytes_]
    $traceGoodput set bytes_ 0
    set goodput [expr ($nbytes * 8.0 / 1000000)]

    # writing cwnd, rtt and goodput for this time unit in output file
    puts $outputFile "$now\t$cwnd\t$rtt\t$goodput"

    # calling writeInOutputFile recursively after 1 second
    $ns at [expr $now + 1] "writeInOutputFile $tcpSource $traceGoodput $outputFile"
}

# declaring a new instance of class TraceGoodput
set traceGoodput1 [new TraceGoodput]

# attaching traceGoodput1 to sink5
$traceGoodput1 attach-agent $sink5

# Start the traceGoodput1 object at time 0
$ns  at  0.0  "$traceGoodput1  start";

# writing headers in output file of tcp1 variables
puts $variableTraceFile1 "time\tcwnd\trtt\tgoodput"

# calling writeInOutputFile proc to write desired parameters in output file for tcp1
$ns at 0.0 "writeInOutputFile $tcp1 $traceGoodput1 $variableTraceFile1"


# declaring a new instance of class TraceGoodput
set traceGoodput2 [new TraceGoodput]

# attaching traceGoodput2 to sink6
$traceGoodput2 attach-agent $sink6

# Start the traceGoodput2 object at time 0
$ns  at  0.0  "$traceGoodput2  start";

# writing headers in output file of tcp2 variables
puts $variableTraceFile2 "time\tcwnd\trtt\tgoodput"

# calling writeInOutputFile proc to write desired parameters in output file for tcp2
$ns at 0.0 "writeInOutputFile $tcp2 $traceGoodput2 $variableTraceFile2"

# Run the simulation
$ns run 
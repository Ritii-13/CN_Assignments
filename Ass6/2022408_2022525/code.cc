#include <iostream>
#include <fstream>
#include <string>
#include <cassert>

#include "ns3/core-module.h"

#include "ns3/network-module.h"

#include "ns3/internet-module.h"

#include "ns3/point-to-point-module.h"

#include "ns3/csma-module.h"

#include "ns3/applications-module.h"

#include "ns3/netanim-module.h"

#include "ns3/traffic-control-module.h"

#include "ns3/flow-monitor-module.h"

#include "ns3/flow-monitor-helper.h"

#include "ns3/error-model.h"

#include "ns3/queue-disc.h"

#include "ns3/red-queue-disc.h"


using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Topo");

//
// N1 -- R1 -- R2 -- N2
//        |     |
// N3 -- R3 -- R4 -- N4
//        |
//       N5

// using namespace ns3;

std::ofstream queueFile("queue-lengths.txt");

// Callback function to log queue length
void LogQueueLength(Ptr<QueueDisc> queueDisc, Ptr<const QueueItem> item)
{
    // Get the current queue size (in bytes)
    QueueSize queueSize = queueDisc->GetCurrentSize();

    // Convert it to uint32_t (bytes)
    uint32_t queueSizeInBytes = queueSize.GetValue();  // `GetValue()` returns the size in bytes
    
    std::cout << "Queue size: " << queueSizeInBytes << " bytes" << std::endl;
}


int main(int argc, char *argv[]) {
    CommandLine cmd;
    cmd.Parse(argc, argv);

    // Create Nodes
    NodeContainer hosts;
    hosts.Create(5);  // N1, N2, N3, N4, N5

    NodeContainer routers;
    routers.Create(4);  // R1, R2, R3, R4

    // Define Point-to-Point Links with Different Capacities
    PointToPointHelper p2p_1mbps, p2p_2mbps, p2p_2_5mbps, p2p_3mbps, p2p_1_5mbps;

    // Configure Data Rates
    p2p_1mbps.SetDeviceAttribute("DataRate", StringValue("1Mbps"));
    p2p_1mbps.SetChannelAttribute("Delay", StringValue("1ms"));

    p2p_2mbps.SetDeviceAttribute("DataRate", StringValue("2Mbps"));
    p2p_2mbps.SetChannelAttribute("Delay", StringValue("1ms"));

    p2p_2_5mbps.SetDeviceAttribute("DataRate", StringValue("2.5Mbps"));
    p2p_2_5mbps.SetChannelAttribute("Delay", StringValue("1ms"));

    p2p_3mbps.SetDeviceAttribute("DataRate", StringValue("3Mbps"));
    p2p_3mbps.SetChannelAttribute("Delay", StringValue("1ms"));

    p2p_1_5mbps.SetDeviceAttribute("DataRate", StringValue("1.5Mbps"));
    p2p_1_5mbps.SetChannelAttribute("Delay", StringValue("1ms"));

    // Install Links Between Hosts and Routers
    NetDeviceContainer n1r1 = p2p_1mbps.Install(NodeContainer(hosts.Get(0), routers.Get(0)));  // N1 -- R1
    NetDeviceContainer n2r2 = p2p_1mbps.Install(NodeContainer(hosts.Get(1), routers.Get(1)));  // N2 -- R2
    NetDeviceContainer n3r3 = p2p_3mbps.Install(NodeContainer(hosts.Get(2), routers.Get(2)));  // N3 -- R3
    NetDeviceContainer n4r4 = p2p_1mbps.Install(NodeContainer(hosts.Get(3), routers.Get(3)));  // N4 -- R4
    NetDeviceContainer n5r3 = p2p_1mbps.Install(NodeContainer(hosts.Get(4), routers.Get(2)));  // N5 -- R3

    // Install Links Between Routers with Specified Capacities
    NetDeviceContainer r1r2 = p2p_3mbps.Install(NodeContainer(routers.Get(0), routers.Get(1)));  // R1 -- R2 (3 Mbps)
    NetDeviceContainer r1r3 = p2p_2_5mbps.Install(NodeContainer(routers.Get(0), routers.Get(2)));  // R1 -- R3 (2.5 Mbps)
    NetDeviceContainer r2r4 = p2p_1mbps.Install(NodeContainer(routers.Get(1), routers.Get(3)));  // R2 -- R4 (1 Mbps)
    NetDeviceContainer r3r4 = p2p_1_5mbps.Install(NodeContainer(routers.Get(2), routers.Get(3)));  // R3 -- R4 (1.5 Mbps)

    // Add Error Model to Simulate Packet Drops
    // Ptr<RateErrorModel> errorModel = CreateObject<RateErrorModel>();
    // errorModel->SetRate(0.005);  // 0.5% drop rate
    // for (auto device : {n1r1, n2r2, n3r3, n4r4, n5r3, r1r2, r1r3, r2r4, r3r4}) {
    //     device.Get(1)->SetAttribute("ReceiveErrorModel", PointerValue(errorModel));
    // }

    // Inside your main function, after device installation:
    // TrafficControlHelper tch;
    // tch.SetRootQueueDisc("ns3::RedQueueDisc");  // Ensure correct QueueDisc type
    // for (auto device : {n1r1, n2r2, n3r3, n4r4, n5r3, r1r2, r1r3, r2r4, r3r4}) {
    //     Ptr<NetDevice> dev = device.Get(1);
    //     tch.Install(dev);  // Ensure that queue discipline is installed correctly
    // }


    // Install Internet Stack
    InternetStackHelper internet;
    internet.Install(hosts);
    internet.Install(routers);

    // Assign IP Addresses to Each Link
    Ipv4AddressHelper ipv4;

    ipv4.SetBase("10.1.1.0", "255.255.255.0");
    ipv4.Assign(n1r1);

    ipv4.SetBase("10.1.2.0", "255.255.255.0");
    ipv4.Assign(n2r2);

    ipv4.SetBase("10.1.3.0", "255.255.255.0");
    ipv4.Assign(n3r3);

    ipv4.SetBase("10.1.4.0", "255.255.255.0");
    ipv4.Assign(n4r4);

    ipv4.SetBase("10.1.5.0", "255.255.255.0");
    ipv4.Assign(n5r3);

    ipv4.SetBase("10.1.6.0", "255.255.255.0");
    ipv4.Assign(r1r2);

    ipv4.SetBase("10.1.7.0", "255.255.255.0");
    ipv4.Assign(r1r3);

    ipv4.SetBase("10.1.8.0", "255.255.255.0");
    ipv4.Assign(r2r4);

    ipv4.SetBase("10.1.9.0", "255.255.255.0");
    ipv4.Assign(r3r4);

    // Populate Routing Tables
    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    // Add Queue Monitor
    Ptr<QueueDisc> queueDisc;
    for (auto device : {n1r1, n2r2, n3r3, n4r4, n5r3, r1r2, r1r3, r2r4, r3r4}) {
        queueDisc = device.Get(1)->GetObject<QueueDisc>();
        if (queueDisc != nullptr) {
            queueDisc->TraceConnectWithoutContext("Enqueue", MakeCallback(&LogQueueLength));
        }
    }

    // Applications
    uint16_t port = 9;

    // UDP Echo Server on N3
    UdpEchoServerHelper echoServer(port);
    ApplicationContainer serverApps = echoServer.Install(hosts.Get(2));  // N4
    serverApps.Start(Seconds(1.0));
    serverApps.Stop(Seconds(58.0));

    // UDP Clients with Poisson Traffic Matrix
    double trafficMatrix[5][5] = {
        {0, 120, 132, 144, 160},
        {100, 0, 190, 111, 154},
        {101, 100, 0, 199, 108},
        {150, 156, 262, 0, 159},
        {140, 188, 285, 171, 0}
    };

    // UDP Echo Clients on N1, N2, N3, N5
    ApplicationContainer clientApps;
    for (int src = 0; src < 5; ++src) {
        for (int dst = 0; dst < 5; ++dst) {
            if (src != dst && src != 2) {
                // Destination IP Address (assuming N4 is the server, adjust dynamically if needed)
                Ipv4Address destIp = Ipv4Address("10.1.3.1");  // Destination IP based on topology

                // Configure OnOffHelper with traffic rate and mean from the matrix
                OnOffHelper client("ns3::UdpSocketFactory",
                    InetSocketAddress(destIp, port));

                // Set the data rate and packet size (2048 bits = 256 bytes)
                client.SetConstantRate(DataRate("2048b/s"), 2048);

                // Use the traffic matrix value as the mean for the OnTime exponential distribution
                double meanTraffic = trafficMatrix[src][dst];
                std::ostringstream onTimeValue;
                onTimeValue << "ns3::ExponentialRandomVariable[Mean=" << meanTraffic << "]";
                client.SetAttribute("OnTime", StringValue(onTimeValue.str()));

                // OffTime can be adjusted separately, e.g., for idle periods (optional)
                client.SetAttribute("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0.5]"));

                // Install the client on the source node
                clientApps.Add(client.Install(hosts.Get(src)));
            }
        }
    }
    clientApps.Start(Seconds(2.0));
    clientApps.Stop(Seconds(59.0));

    // Enable Tracing for Each Link
    p2p_1mbps.EnablePcapAll("topology-1mbps");
    p2p_2mbps.EnablePcapAll("topology-2mbps");
    p2p_2_5mbps.EnablePcapAll("topology-2.5mbps");
    p2p_3mbps.EnablePcapAll("topology-3mbps");
    p2p_1_5mbps.EnablePcapAll("topology-1.5mbps");

    // Enable flow monitor
    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> monitor = flowmonHelper.InstallAll();

    // Trace Routing Tables
    Ipv4GlobalRoutingHelper g;
    Ptr<OutputStreamWrapper> routingStream = Create<OutputStreamWrapper>("topo.routes", std::ios::out);
    g.PrintRoutingTableAllAt(Seconds(1), routingStream);

    // Animation Interface
    AnimationInterface anim("topo.xml");
    anim.SetConstantPosition(hosts.Get(0), 10, 50);  // N1
    anim.SetConstantPosition(routers.Get(0), 30, 50);  // R1
    anim.SetConstantPosition(routers.Get(1), 50, 50);  // R2
    anim.SetConstantPosition(hosts.Get(1), 70, 50);  // N2

    anim.SetConstantPosition(hosts.Get(2), 10, 30);  // N3
    anim.SetConstantPosition(routers.Get(2), 30, 30);  // R3
    anim.SetConstantPosition(routers.Get(3), 50, 30);  // R4
    anim.SetConstantPosition(hosts.Get(3), 70, 30);  // N4

    anim.SetConstantPosition(hosts.Get(4), 30, 10);  // N5

    // Enable ASCII Tracing for Each Link
    AsciiTraceHelper ascii;
    p2p_1mbps.EnableAsciiAll(ascii.CreateFileStream("topology-1mbps.tr"));
    p2p_2mbps.EnableAsciiAll(ascii.CreateFileStream("topology-2mbps.tr"));
    p2p_2_5mbps.EnableAsciiAll(ascii.CreateFileStream("topology-2.5mbps.tr"));
    p2p_3mbps.EnableAsciiAll(ascii.CreateFileStream("topology-3mbps.tr"));
    p2p_1_5mbps.EnableAsciiAll(ascii.CreateFileStream("topology-1.5mbps.tr"));

    // Run Simulation
    Simulator::Stop(Seconds(60.0));
    Simulator::Run();

    // ipv4.PrintRoutingTableAll();

    // Print Flow Monitor Statistics
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());
    std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats();

    std::ofstream statsFile("simulation-stats.txt");
    statsFile << "FlowID\tSource\tDestination\tTxPackets\tRxPackets\tLostPackets\tTxBytes\tRxBytes\tThroughput(bps)\tAvgDelay(s)\n";

    for (auto &flow : stats) {
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(flow.first);
        std::cout << "Flow " << flow.first << ": " << t.sourceAddress << " -> " << t.destinationAddress << std::endl;

        double throughput = (flow.second.rxBytes * 8.0) / (flow.second.timeLastRxPacket.GetSeconds() - flow.second.timeFirstTxPacket.GetSeconds());
        double avgDelay = flow.second.rxPackets > 0
                        ? (flow.second.delaySum.GetSeconds() / flow.second.rxPackets)
                        : 0.0;

        statsFile << flow.first << "\t"
                << t.sourceAddress << "\t"
                << t.destinationAddress << "\t"
                << flow.second.txPackets << "\t"
                << flow.second.rxPackets << "\t"
                << flow.second.lostPackets << "\t"
                << flow.second.txBytes << "\t"
                << flow.second.rxBytes << "\t"
                << throughput << "\t"
                << avgDelay << "\n";
    }
    statsFile.close();


    // Serialize monitor data to XML for visualization
    try {
        monitor->SerializeToXmlFile("flow-monitor.xml", true, true);
    } catch (const std::exception &e) {
        NS_LOG_ERROR("Error serializing Flow Monitor data: " << e.what());
    }

    Simulator::Destroy();

    return 0;
}

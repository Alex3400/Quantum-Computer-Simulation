import math

import matplotlib.pyplot as plt
from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import pylatexenc
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_state_city, plot_bloch_multivector
from qiskit.visualization import plot_state_paulivec, plot_state_hinton
from qiskit.visualization import plot_state_qsphere
import seaborn
from qiskit.circuit import Gate
import random


def calc(qc):
    backend = BasicAer.get_backend('qasm_simulator')
    j = backend.run(transpile(qc, backend)).result()
    print(j.get_counts(qc))


def numberone():
    simulator = AerSimulator()

    circuit = QuantumCircuit(2, 2)

    circuit.h(0)

    circuit.cx(0, 1)

    circuit.measure([0], [0])

    compiled_circuit = transpile(circuit, simulator)

    job = simulator.run(compiled_circuit, shots=10, memory = True)

    result = job.result()

    counts = result.get_memory(compiled_circuit)
    print("\nTotal count for 00 and 11 are:", counts)

    # Draw the circuit
    circuit.draw("mpl")
    plt.show()
    circuit.draw()


def numbertwo():
    bell = QuantumCircuit(2, 2)
    bell.h(0)
    bell.cx(0, 1)

    meas = QuantumCircuit(2, 2)
    meas.measure([0, 1], [0, 1])

    # execute the quantum circuit
    backend = BasicAer.get_backend('qasm_simulator')  # the device to run on
    circ = bell.compose(meas)
    result = backend.run(transpile(circ, backend), shots=1000).result()
    counts = result.get_counts(circ)
    print(counts)
    plot_histogram(counts)
    # plt.show()
    second_result = backend.run(transpile(circ, backend), shots=1000).result()
    second_counts = second_result.get_counts(circ)
    backend = BasicAer.get_backend('statevector_simulator')  # the device to run on
    result = backend.run(transpile(bell, backend)).result()
    psi = result.get_statevector(bell)
    plot_state_qsphere(psi)
    plt.show()


def numberthree():
    q = QuantumRegister(3)
    c = ClassicalRegister(3)
    qc = QuantumCircuit(q, c)
    qc.h(q[0])
    qc.h(q[1])
    qc.ccx(q[0], q[1], q[2])
    qc.measure(q, c)
    calc(qc)
    qc.draw("mpl")
    plt.show()


def numberfour():
    my_gate = Gate(name='my_gate', num_qubits=2, params=[])
    qr = QuantumRegister(3)
    cr = ClassicalRegister(3)
    circ = QuantumCircuit(qr, cr)
    circ.append(my_gate, [qr[0], qr[1]])
    circ.append(my_gate, [qr[1], qr[2]])

    sub_q = QuantumRegister(2)
    sub_c = ClassicalRegister(2)
    sub_circ = QuantumCircuit(sub_q, sub_c)
    sub_circ.measure(sub_q, sub_c)

    sub_inst = sub_circ.to_instruction()

    circ.append(sub_inst, [qr[1], qr[2]])

    circ.draw()
    circ.draw("mpl")
    plt.show()


def bb84(key, percentTest):
    eve = random.random() < 0.75
    n = len(key)
    q = QuantumRegister(n)
    c = ClassicalRegister(n)
    qc = QuantumCircuit(q, c)
    polA = []
    polB = []
    polE = []
    for i in range(n):
        if random.random() < 0.5:
            polA.append(0)
        else:
            polA.append(1)
        if random.random() > 0.5:
            polB.append(0)
        else:
            polB.append(1)
        if random.random() > 0.5:
            polE.append(0)
        else:
            polE.append(1)
    for k in range(len(key)):
        if key[k] == 1:
            qc.x(q[k])
    qc.barrier()
    for k in range(len(key)):
        if polA[k] == 1:
            qc.h(q[k])
    qc.barrier()
    if eve:
        for k in range(len(key)):
            if polE[k] == 1:
                qc.h(q[k])
                qc.measure(q[k], c[k])
                qc.h(q[k])
            else:
                qc.measure(q[k], c[k])
    qc.barrier()
    for k in range(len(key)):
        if polB[k] == 1:
            qc.h(q[k])
    qc.barrier()
    qc.measure(q, c)

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)

    job = simulator.run(compiled_circuit, shots=1, memory=True)
    r = job.result().get_memory(compiled_circuit)[0]
    results = []
    for k in range(len(key)):
        results.append(int(r[k]))
    results.reverse()
    for k in range(len(key)):
        if polA[k] != polB[k]:
            results[k] = 7
            key[k] = 7
    results = list(filter((7).__ne__, results))
    key = list(filter((7).__ne__, key))

    testBits = math.floor(percentTest * len(results))
    caught = False
    for j in range(testBits):
        if key[j] != results[j]:
            caught = True
            break


    qc.draw()
    qc.draw("mpl")
    plt.show()

    # print(key) # printing the string of bits initially given
    # print(results) # printing the results of the observation by bob
    # print(polA) #printing the random choice of polarization taken by Alice, 1 for 45, 135, 0 for 0,90
    # print(polB) #similarly for bob
    #
    # for k in range(len(key)):
    #     if polA[k] != polB[k]:
    #         results[k] = 7
    # print(results) #priting the results of the observation with the bits where the polarization was different wiht a 7
    # print(list(filter((7).__ne__, results))) # priting the sequence of bits attained by both Alice and Bob
    return(results, testBits, eve, caught)


if __name__ == '__main__':
    avglength = 0
    avgTest = 0
    intCaught = 0
    intNotCaught = 0

    bits = 10
    tests = 1
    testPercent = 0.3

    for t in range(tests):
        test = []
        for x in range(bits):
            if random.random() < 0.5:
                test.append(0)
            else:
                test.append(1)
        r = bb84(test, testPercent)
        s = ""
        avglength += len(r[0])
        avgTest += r[1]
        if r[2] and r[3]:
            s = "there was interfernce and it was detected"
            intCaught += 1
        elif r[2] and not r[3]:
            s = "there was interference and it wasn't detected"
            intNotCaught += 1
        elif not r[2]:
            s = "there was no interference"
        # print("test number " + str(t) + ":, key is: " + str(r[0]) + ", of length "
        #       + str(len(r[0])) + ", testBits used: " + str(r[1]) + ", " + s)
    print()
    print("with " + str(bits) + " bits the key had an average length of " + str(avglength/tests) + " with an average of " + str(avgTest/tests) + " bits being used to detect interference over " + str(tests) + " tests")
    print(str(math.floor(10000 * intCaught/(intCaught + intNotCaught))/100) + "% of interferences were caught with " + str(intCaught) + " interferences caught and " + str(intNotCaught) + " interferences not caught" )


d=1; // grating period
ff = 0.305280;
d_in_nm = 1200;
a1 = 290;
a2 = 110;
a3 = 131;
a4 = 163;
radius1 = (a1/d_in_nm)*d;
radius2 = (a2/d_in_nm)*d;
radius3 = (a3/d_in_nm)*d;
radius4 = (a4/d_in_nm)*d;
lc = 0.090000; // 0.501 0.201 0.0701;
lc2 = lc/1.900000; // on cylinder surfaces
lc3 = lc/1.100000; // cylinder1 centres
lc4 = lc/4.500000; // cylinder2 centres
lc5 = lc/1.800000; // cylinder3 centres
lc6 = lc/1.100000; // cylinder4 centres

hy = d; // Thickness: Squre profile => hy=d
hx = 0.;

// 2*2 supercell outline

Point(1) = {0, 0, 0, lc};
Point(2) = {-hx, -hy, 0, lc};
Point(3) = {-hx+d, -hy, 0, lc};
Point(4) = {d, 0, 0,lc};
Point(5) = {-hx+d/2., -hy/2., 0,lc};
Point(10) = {-hx+d/2., 0, 0, lc};
Point(11) = {0,-hy/2., 0, lc};
Point(12) = {-hx+d/2., -hy, 0, lc};
Point(13) = {d, -hy/2, 0, lc};

Point(14) = {-hx+d/4., 0, 0, lc};
Point(15) = {-hx+d*3/4., 0, 0, lc};
Point(16) = {0,-hy/4., 0, lc};
Point(18) = {d/2,-hy/4., 0, lc};
Point(20) = {d,-hy/4., 0, lc};
Point(21) = {-hx+d/4., -hy/2., 0,lc};
Point(22) = {-hx+d*3/4., -hy/2., 0,lc};
Point(23) = {0,-hy*3/4., 0, lc};
Point(25) = {d/2,-hy*3/4., 0, lc};
Point(27) = {d,-hy*3/4., 0, lc};
Point(28) = {-hx+d/4., -hy, 0, lc};
Point(29) = {-hx+d*3/4., -hy, 0, lc};

// circle - top left
Point(17) = {d/4,-hy/4., 0, lc3};
Point(30) = {-hx+d/4., -hy/4.+radius1, 0, lc2};
Point(31) = {-hx+d/4.-radius1, -hy/4., 0, lc2};
Point(32) = {-hx+d/4., -hy/4.-radius1, 0, lc2};
Point(33) = {-hx+d/4.+radius1, -hy/4., 0, lc2};
// circle - top right
Point(19) = {d*3/4,-hy/4., 0, lc4};
Point(34) = {-hx+d*3/4., -hy/4.+radius2, 0, lc2};
Point(35) = {-hx+d*3/4.-radius2, -hy/4., 0, lc2};
Point(36) = {-hx+d*3/4., -hy/4.-radius2, 0, lc2};
Point(37) = {-hx+d*3/4.+radius2, -hy/4., 0, lc2};
// circle - bottom left
Point(24) = {d/4,-hy*3/4., 0, lc5};
Point(38) = {-hx+d/4., -hy*3/4.+radius3, 0, lc2};
Point(39) = {-hx+d/4.-radius3, -hy*3/4., 0, lc2};
Point(40) = {-hx+d/4., -hy*3/4.-radius3, 0, lc2};
Point(41) = {-hx+d/4.+radius3, -hy*3/4., 0, lc2};
// circle - bottom right
Point(26) = {d*3/4,-hy*3/4., 0, lc6};
Point(42) = {-hx+d*3/4., -hy*3/4.+radius4, 0, lc2};
Point(43) = {-hx+d*3/4.-radius4, -hy*3/4., 0, lc2};
Point(44) = {-hx+d*3/4., -hy*3/4.-radius4, 0, lc2};
Point(45) = {-hx+d*3/4.+radius4, -hy*3/4., 0, lc2};

Line(1) = {1, 14};
Line(2) = {14, 10};
Line(3) = {10, 15};
Line(4) = {15, 4};
Line(5) = {4, 20};
Line(6) = {20, 13};
Line(7) = {13, 27};
Line(8) = {27, 3};
Line(9) = {3, 29};
Line(10) = {29, 12};
Line(11) = {12, 28};
Line(12) = {28, 2};
Line(13) = {2, 23};
Line(14) = {23, 11};
Line(15) = {11, 16};
Line(16) = {16, 1};
Line(18) = {18, 10};
Line(19) = {18, 5};
Line(20) = {5, 25};
Line(21) = {25, 12};
Line(22) = {11, 21};
Line(23) = {21, 5};
Line(24) = {5, 22};
Line(25) = {22, 13};
Line(26) = {14, 30};
Line(27) = {30, 17};
Line(28) = {17, 32};
Line(29) = {32, 21};
Line(30) = {16, 31};
Line(31) = {31, 17};
Line(32) = {17, 33};
Line(33) = {33, 18};
Line(34) = {15, 34};
Line(35) = {34, 19};
Line(36) = {19, 36};
Line(37) = {36, 22};
Line(38) = {18, 35};
Line(39) = {35, 19};
Line(40) = {19, 37};
Line(41) = {37, 20};
Line(42) = {21, 38};
Line(43) = {38, 24};
Line(44) = {24, 40};
Line(45) = {40, 28};
Line(46) = {23, 39};
Line(47) = {39, 24};
Line(48) = {24, 41};
Line(49) = {41, 25};
Line(50) = {22, 42};
Line(51) = {42, 26};
Line(52) = {26, 44};
Line(53) = {44, 29};
Line(54) = {25, 43};
Line(55) = {43, 26};
Line(56) = {26, 45};
Line(57) = {45, 27};

Circle(58) = {30, 17, 33};
Circle(59) = {33, 17, 32};
Circle(60) = {32, 17, 31};
Circle(61) = {31, 17, 30};
Circle(62) = {34, 19, 37};
Circle(63) = {37, 19, 36};
Circle(64) = {36, 19, 35};
Circle(65) = {35, 19, 34};
Circle(66) = {38, 24, 41};
Circle(67) = {41, 24, 40};
Circle(68) = {40, 24, 39};
Circle(69) = {39, 24, 38};
Circle(70) = {42, 26, 45};
Circle(71) = {45, 26, 44};
Circle(72) = {44, 26, 43};
Circle(73) = {43, 26, 42};

Line Loop(76) = {1, 26, -61, -30, 16};
Plane Surface(77) = {76};
Line Loop(78) = {2, -18, -33, -58, -26};
Plane Surface(79) = {78};
Line Loop(80) = {33, 19, -23, -29, -59};
Plane Surface(81) = {80};
Line Loop(82) = {22, -29, 60, -30, -15};
Plane Surface(83) = {82};
Line Loop(84) = {58, -32, -27};
Plane Surface(85) = {84};
Line Loop(86) = {59, -28, 32};
Plane Surface(87) = {86};
Line Loop(88) = {60, 31, 28};
Plane Surface(89) = {88};
Line Loop(90) = {31, -27, -61};
Plane Surface(91) = {90};
Line Loop(92) = {3, 34, -65, -38, 18};
Plane Surface(93) = {92};
Line Loop(94) = {34, 62, 41, -5, -4};
Plane Surface(95) = {94};
Line Loop(96) = {41, 6, -25, -37, -63};
Plane Surface(97) = {96};
Line Loop(98) = {37, -24, -19, 38, -64};
Plane Surface(99) = {98};
Line Loop(100) = {62, -40, -35};
Plane Surface(101) = {100};
Line Loop(102) = {40, 63, -36};
Plane Surface(103) = {102};
Line Loop(104) = {36, 64, 39};
Plane Surface(105) = {104};
Line Loop(106) = {39, -35, -65};
Plane Surface(107) = {106};
Line Loop(108) = {25, 7, -57, -70, -50};
Plane Surface(109) = {108};
Line Loop(110) = {57, 8, 9, -53, -71};
Plane Surface(111) = {110};
Line Loop(112) = {53, 10, -21, 54, -72};
Plane Surface(113) = {112};
Line Loop(114) = {54, 73, -50, -24, 20};
Plane Surface(115) = {114};
Line Loop(116) = {70, -56, -51};
Plane Surface(117) = {116};
Line Loop(118) = {71, -52, 56};
Plane Surface(119) = {118};
Line Loop(120) = {52, 72, 55};
Plane Surface(121) = {120};
Line Loop(122) = {55, -51, -73};
Plane Surface(123) = {122};
Line Loop(124) = {22, 42, -69, -46, 14};
Plane Surface(125) = {124};
Line Loop(126) = {23, 20, -49, -66, -42};
Plane Surface(127) = {126};
Line Loop(128) = {49, 21, 11, -45, -67};
Plane Surface(129) = {128};
Line Loop(130) = {45, 12, 13, 46, -68};
Plane Surface(131) = {130};
Line Loop(132) = {66, -48, -43};
Plane Surface(133) = {132};
Line Loop(134) = {48, 67, -44};
Plane Surface(135) = {134};
Line Loop(136) = {44, 68, 47};
Plane Surface(137) = {136};
Line Loop(138) = {47, -43, -69};
Plane Surface(139) = {138};

Physical Line(140) = {1, 2, 3, 4};
Physical Line(141) = {5, 6, 7, 8};
Physical Line(142) = {9, 10, 11, 12};
Physical Line(143) = {13, 14, 15, 16};

Physical Surface(3) = {77, 79, 81, 83, 93, 95, 97, 99, 125, 127, 129, 131, 115, 109, 111, 113};
Physical Surface(4) = {91, 85, 87, 89};
Physical Surface(5) = {107, 101, 103, 105, 117, 119, 121, 123, 133, 135, 137, 139};
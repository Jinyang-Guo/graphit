//
// Created by Yunming Zhang on 2/14/17.
//

#include <gtest.h>

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);

    //::testing::GTEST_FLAG(filter) = "LexandParseTest.SimpleAdd";
    //::testing::GTEST_FLAG(filter) = "MIRGenTest.*";



    return RUN_ALL_TESTS();
}
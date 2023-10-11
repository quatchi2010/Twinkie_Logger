cmake_minimum_required(VERSION 3.10)

project(
	twinkie_console
	VERSION 0.0.1
	DESCRIPTION "TwinkieV2 Console Application")

include_directories(include)

set(SOURCES
	src/crc32.c
	src/log.c
	src/discover.c
	src/device.c
	src/snooper_stream.c
	src/twinkie_console.c)

add_executable(twinkie_console ${SOURCES})

find_package(Threads REQUIRED)
target_link_libraries(twinkie_console Threads::Threads)
target_link_libraries(twinkie_console pthread)

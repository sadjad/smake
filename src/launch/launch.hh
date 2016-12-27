/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 2 -*- */

#include <string>
#include <vector>

void launchpar(size_t nlaunch,
               std::string fn_name,
               std::string akid,
               std::string secret,
               std::vector<std::string> payloads,
               std::vector<std::string> lambda_regions);

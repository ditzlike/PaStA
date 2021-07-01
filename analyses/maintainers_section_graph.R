#!/usr/bin/env Rscript

# PaStA - Patch Stack Analysis
#
# Copyright (c) OTH Regensburg, 2019-2020
#
# Author:
#   Ralf Ramsauer <ralf.ramsauer@oth-regensburg.de>
#   Pia Eichinger <pia.eichinger@st.oth-regensburg.de>
#
# This work is licensed under the terms of the GNU GPL, version 2.  See
# the COPYING file in the top-level directory.

library("igraph")
library("RColorBrewer")
source("analyses/util.R")

# delete all vertices below this quantile
VERTEX_QUANTILE <- '0%'
# delete all edges below this quantile, also used for linder edge density layout
EDGE_QUANTILE <- '0%'

PALETTE <- c('#D83359','#979CFB','#f46d43','#fdae61','#fee090','#ffffbf','#e0f3f8','#abd9e9','#74add1','#4575b4','#d73027')

PRINT_ENTIRE_GRAPH <- TRUE
PRINT_CLUSTERS <- TRUE
PRINT_RANDOM_CLUSTERS <- FALSE

VERTEX_SIZE <- 0.5
LABEL_SIZE <- 0.6

# minimum size of nodes in printed clusters
MIN_CLUSTERSIZE <- 20
# maximum size of nodes in printed clusters
MAX_CLUSTERSIZE <- 100
FONT_FAMILY <- "Helvetica"

PRINT_DEGREE_INFO <- FALSE
PRINT_INFORMATION <- FALSE
DISPLAY_LABELS <- FALSE

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  file_name <- file.path(d_resources, 'maintainers_section_graph', 'HEAD.csv')
} else {
  file_name <- args[1]
}

d_maintainers_cluster <- file.path(d_resources, 'maintainers_cluster')
dir.create(d_maintainers_cluster, showWarnings = FALSE)
CLUSTER_DESTINATION <- file.path(d_maintainers_cluster,
                                 gsub(".csv$", ".txt", basename(file_name)))
TIKZ_DESTINATION <- file.path(d_resources, gsub(".tex$", ".txt",
						basename(file_name)))

data_frame <- read_csv(file_name)
data_frame$weight <- data_frame$lines

g  <- igraph::graph_from_data_frame(data_frame, directed = FALSE)

# We need to remove THE REST because it's trivial that this section contains
# everything. In case of QEMU, since this node is QEMU's equivalent of THE REST
# whereas THE REST doesn't exist, we need to remove General Project
# Administration instead
if (project == 'qemu') {
  g <- igraph::delete.vertices(g, which(grepl("General Project Administration",
                                            V(g)$name)))
} else {
  g <- igraph::delete.vertices(g, "THE REST")
}

# retrieve vertex size by finding edge weight of self loop
for (e in which(which_loop(g))) {
  assertthat::are_equal(head_of(g, E(g)[e]), tail_of(g, E(g)[e]))
  my_vertex <- head_of(g, E(g)[e])
  edge_weight <- E(g)[e]$weight
  g <- igraph::set.vertex.attribute(g, "size", my_vertex, edge_weight)
}

# delete all self loops
g <- simplify(g, remove.multiple = TRUE, remove.loops = TRUE)

probes <- seq(0, 1, 0.05)

global_edge_quantiles <- quantile(E(g)$weight, probs=probes)
global_vertex_quantiles <- quantile(V(g)$size, probs=probes)

print_graph_information <- function(param) {
  print("Number of vertices:")
  print(length(V(g)))

  print("Average vertex size")
  print(mean(V(g)$size))

  print("Number of edges")
  print(length(E(g)))

  print("Average edge weight")
  print(mean(E(g)$weight))

  deg <- igraph::degree(param)
  deg <- sort(deg, decreasing = TRUE)

  if (!PRINT_DEGREE_INFO) {
    return()
  }

  print("Top 10 Sections with highest degree:")
  for (j in seq(1, 10, 1)) {
    print(deg[j])
  }

  deg <- sort(deg)

  print("All isolated sections:")
  i <- 1
  while(unname(deg[i]) == 0) {
    print(deg[i])
    i <- i+1
  }

  deg <- sort(deg)

  print("Average degree including isolates:")
  print(mean(deg))

  stats_graph <- igraph::delete.vertices(g, igraph::degree(param)==0)
  print("Average degree exluding isolates:")
  print(mean(igraph::degree(stats_graph)))
}

print_graph_information(g)

# deleting all vertices and edges that are below the specified quantile
g <- igraph::delete.vertices(g, which(V(g)$size < unname(global_vertex_quantiles[VERTEX_QUANTILE])))
g <- igraph::delete.edges(g, which(E(g)$weight < unname(global_edge_quantiles[EDGE_QUANTILE])))

# in case of Linux delete all entries with DRIVER
#if (project == 'linux') {
#  g <- igraph::delete.vertices(g, V(g)[grepl("DRIVER", toupper(V(g)$name))])
#}

wt_comm <- cluster_walktrap(g)
V(g)$comm <- membership(wt_comm)

# deleting all edges and adding new ones only within clusters
layout_with_cluster_edges <- function(param, attraction) {
  g_grouped <- param
  wt_comm <- cluster_walktrap(param)
  V(g_grouped)$comm <- membership(wt_comm)
  g_grouped <- igraph::delete.edges(g_grouped, E(g_grouped))

  iterate <- seq(1, length(V(g_grouped)), 1)
  for (i in iterate) {
    for (j in iterate) {
      if (i == j) {
        next
      }
      if (V(g_grouped)[i]$comm == V(g_grouped)[j]$comm) {
        g_grouped <- igraph::add.edges(g_grouped, c(i, j), weight=attraction)
      }
    }
  }

  return(layout.fruchterman.reingold(g_grouped, niter = 500))
}

if (PRINT_ENTIRE_GRAPH) {
  LO = layout_with_cluster_edges(g, 0.1)
  printplot(g, 'complete_graph_labels',
              mark.groups = igraph::groups(wt_comm),
              mark.col = PALETTE,
              vertex.size = VERTEX_SIZE,
              vertex.label.dist = 0.5,
              vertex.label.cex = LABEL_SIZE,
              vertex.label.family = FONT_FAMILY,
              layout = LO
              )

  printplot(g, 'complete_graph',
              mark.groups = igraph::groups(wt_comm),
              mark.col = PALETTE,
              vertex.size = VERTEX_SIZE,
              vertex.label = NA,
              layout = LO
              )
}

comm_groups <- igraph::groups(wt_comm)
bounds <- seq(1, length(comm_groups), 1)

if (PRINT_CLUSTERS) {
  # save each cluster community as own plot clustered again from within
  for (i in bounds) {
    group <- comm_groups[i]
    group_list <- unname(group)[[1]]

    if (!is.na(MIN_CLUSTERSIZE) && length(group_list) < MIN_CLUSTERSIZE) {
      next
    }

    if (!is.na(MAX_CLUSTERSIZE) && length(group_list) > MAX_CLUSTERSIZE) {
      next
    }
    print(paste0("ITERATION: ", toString(i)))

    #dplyr doesn't work that well in lambda-like functions such as which
    cluster_graph <- igraph::delete_vertices(g, which(!(V(g)$name %in% group_list)))
    if (PRINT_INFORMATION) {
      print_graph_information(cluster_graph)
    }

    wt_clusters <- cluster_walktrap(cluster_graph)
    print_graph_information(cluster_graph)

    printplot(cluster_graph, paste0("cluster_", toString(i)),
                mark.groups=igraph::groups(wt_clusters),
                mark.col = PALETTE,
                vertex.size=VERTEX_SIZE,
                vertex.label.family = FONT_FAMILY,
                vertex.label.dist=0.5,
                vertex.label.cex=LABEL_SIZE,
                layout = layout_with_cluster_edges(cluster_graph, 0.01)
                )
  }
}

write_cluster_file <- function(g, dst) {
  for (name in names(comm_groups)) {
    comm_groups[[name]] <- sort(comm_groups[[name]])
  }
  sorted_comm_groups <- comm_groups[order(sapply(comm_groups,function(x) x[[1]]))]
  sink(dst)

  for (i in bounds) {
    group <- sorted_comm_groups[i]
    group_list <- unname(group)[[1]]

    for (section in group_list) {
      cat(section)
      cat('\n')
    }
    cat('\n')
  }
  sink()
}

write_cluster_file(g, CLUSTER_DESTINATION)

if (PRINT_RANDOM_CLUSTERS) {
  vertex_names <- V(g)$name

  for (i in bounds){
    group <- comm_groups[i]
    group_list <- unname(group)[[1]]

    if (!is.na(MIN_CLUSTERSIZE) && length(group_list) < MIN_CLUSTERSIZE) {
      next
    }

    if (!is.na(MAX_CLUSTERSIZE) && length(group_list) > MAX_CLUSTERSIZE) {
      next
    }

    # get a random sample of vertex names, as much as we need for the cluster
    name_sample <- sample(vertex_names, length(group_list), replace=FALSE)
    # extract them from the original vertex name vector
    vertex_names <- setdiff(vertex_names, name_sample)

    cluster_graph <- igraph::delete_vertices(g, which(!my_in(V(g)$name, group_list)))
    cluster_graph$random_name <- name_sample

    wt_clusters <- cluster_walktrap(cluster_graph)
    print_graph_information(cluster_graph)

    printplot(cluster_graph, paste0("random_cluster_", toString(i)),
                mark.groups=igraph::groups(wt_clusters),
                mark.col = PALETTE,
                vertex.size=VERTEX_SIZE,
                vertex.label=cluster_graph$random_name,
                vertex.label.family = FONT_FAMILY,
                vertex.label.dist=0.5,
                vertex.label.cex=LABEL_SIZE,
                layout = layout_with_cluster_edges(cluster_graph, 0.01)
                )
  }
}

print_tikz_graph <- function(g, dst) {
  sink(dst)

  # generate trees

  blacklist <- c()
  for (i in bounds) {
    group <- comm_groups[i]
    group_list <- unname(group)[[1]]

    #dplyr doesn't work that well in lambda-like functions such as which
    my_in <- function(vertex) {
      return(vertex %in% group_list)
    }
    cluster_graph <- igraph::delete_vertices(g, which(!my_in(V(g)$name)))
    wt_clusters <- cluster_walktrap(cluster_graph)

    cluster_string <- paste0("tree", toString(i), "[draw,circle] // [simple necklace layout] {")

    if(length(group_list) == 1) {
      #cluster_string <- paste0(cluster_string, '\"', group_list[1], '\"};')
      blacklist <- c(blacklist, i)
      next
    } else {
      for (e in E(cluster_graph)){
        head_node <- tolower(head_of(cluster_graph, e)$name)
        tail_node <- tolower(tail_of(cluster_graph, e)$name)

        if (nchar(head_node) > 16) {
          split <- strsplit(head_node, " ")[[1]]
          #middle <- floor(length(split)/2)
          middle <- ceiling(length(split)/2)
          head_node <- paste0(paste(split[1:middle], collapse = " "), "\\n",
                              paste(split[(middle+1):length(split)], collapse = " "))
        }

        if (nchar(tail_node) > 16) {
          split <- strsplit(tail_node, " ")[[1]]
          middle <- floor(length(split)/2)
          tail_node <- paste0(paste(split[1:middle], collapse = " "), "\\n",
                              paste(split[(middle+1):length(split)], collapse = " "))
        }

        cluster_string <- paste0(cluster_string, '\"', head_node, '\"',
                                 '-- \"', tail_node, '\", ')
      }
      cluster_string <- paste0(substr(cluster_string, 1, nchar(cluster_string)-2), '};')
    }

    cat(cluster_string)
    cat('\n')
  }


  # TODO: there is probably a way better way to do this
  mat <- matrix(0, nrow = length(bounds), ncol = length(bounds))

  for (i in bounds){
    group_i <- comm_groups[i]
    group_list_i <- unname(group_i)[[1]]
    for (j in bounds){
      group_j <- comm_groups[j]
      group_list_j <- unname(group_j)[[1]]
      if (j == i){
        next
      }
      for (v_i in group_list_i){
        for (v_j in group_list_j) {
          #print(g[v_i$name, v_j$name])
          if (g[v_i, v_j] > 0) {
            mat[i, j] = mat[i, j] + 1
          }
        }
      }
    }
  }

  # TODO: take value into account
  # TODO: skip duplicates
  for (i in bounds){
    for (j in bounds){
      if (mat[i, j] != 0) {
        cat(paste0('tree', toString(i), '-- ', 'tree', toString(j)))
        cat('\n')
      }
    }
  }

  sink()
}

print_tikz_graph(g, TIKZ_DESTINATION)

print_tikz_time_cluster <- function(g, dst) {
  sink(dst)

  # TODO: there is probably a way better way to do this
  # first calculate the edges between
  mat <- matrix(0, nrow = length(bounds), ncol = length(bounds))

  for (i in bounds){
    group_i <- comm_groups[i]
    group_list_i <- unname(group_i)[[1]]
    for (j in bounds){
      group_j <- comm_groups[j]
      group_list_j <- unname(group_j)[[1]]
      if (j == i){
        next
      }
      for (v_i in group_list_i){
        for (v_j in group_list_j) {
          #print(g[v_i$name, v_j$name])
          if (g[v_i, v_j] > 0) {
            mat[i, j] = mat[i, j] + 1
          }
        }
      }
    }
  }

  # generate trees and skip the ones with 0 edges in the matrix
  # keep them in mind within the trailing string

  trail_string <- ""
  for (i in bounds) {
    group <- comm_groups[i]
    group_list <- unname(group)[[1]]

    #dplyr doesn't work that well in lambda-like functions such as which
    my_in <- function(vertex) {
      return(vertex %in% group_list)
    }
    cluster_graph <- igraph::delete_vertices(g, which(!my_in(V(g)$name)))
    wt_clusters <- cluster_walktrap(cluster_graph)

    #cluster_string <- paste0("tree", toString(i), "[draw,circle] // [simple necklace layout] {")
    deg <- igraph::degree(cluster_graph)
    maximum_deg <- names(sort(deg, decreasing=TRUE)[1])
    #cluster_string <- paste0("tree", toString(i), "/\"", maximum_deg,
    #                         "\"[draw, circle, minimum size=", length(group_list), "];")

    if (all(mat[,i] == 0)) {
      trail_string <- paste0(trail_string, "tree", toString(i), "/\"", maximum_deg,
                    "\"[draw, circle, minimum size=", length(group_list), "];\n")
    } else {
      cluster_string <- paste0("tree", toString(i), "/\"", maximum_deg,
                             "\"[draw, circle, minimum size=", length(group_list), "];")

    }

    cat(cluster_string)
    cat('\n')
  }
  cat("%%% isolated clusters %%%\n")
  cat(trail_string)


  # TODO: take value into account
  # TODO: skip duplicates
  for (i in bounds){
    for (j in bounds){
      if (mat[i, j] != 0) {
        cat(paste0('tree', toString(i), '--[line width=', mat[i, j], ']',
                   'tree', toString(j), '% size: ', mat[i, j], ';'))
        cat('\n')
      }
    }
  }

  sink()
}

print_tikz_time_cluster(g, TIKZ_DESTINATION)

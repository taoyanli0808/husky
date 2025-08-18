import Vue from 'vue'
import Vuex from 'vuex'
import task from './modules/task'
import requirement from './modules/requirement'
import point from './modules/point'
import testcase from './modules/testcase'

Vue.use(Vuex)

export default function () {
  return new Vuex.Store({
  modules: {
    task,
    requirement,
    point,
    testcase
  },
  strict: process.env.NODE_ENV !== 'production'
  })
}